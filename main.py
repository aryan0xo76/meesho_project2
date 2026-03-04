import os
import uvicorn
import asyncio
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_generator import DataGenerator
from models.covisitation import CovisitationModel
from models.send_time_optimization import SendTimeOptimizer
from models.reranker import CatBoostReranker
from models.headline_generator import HeadlineGenerator

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Meesho Micro-Moments Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models = {
    "covisitation": CovisitationModel(),
    "sto": SendTimeOptimizer(),
    "reranker": CatBoostReranker(),
    "headlines": HeadlineGenerator()
}

class PersonaRequest(BaseModel):
    id: str

def check_data():
    return (DATA_DIR / "events.csv").exists()

def check_models():
    return (DATA_DIR / "catboost_reranker.cbm").exists() and (DATA_DIR / "sto_model.pkl").exists()

@app.get("/api/status")
async def get_status():
    return {
        "data": check_data(),
        "model": check_models()
    }

async def generate_data_bg():
    gen = DataGenerator(DATA_DIR)
    await gen.generate_all_data()

@app.post("/api/generate-data")
async def api_generate_data(bg_tasks: BackgroundTasks):
    bg_tasks.add_task(generate_data_bg)
    return {"status": "started"}

async def train_models_bg():
    try:
        df_events = pd.read_csv(DATA_DIR / "events.csv")
        df_users = pd.read_csv(DATA_DIR / "users.csv")
        df_products = pd.read_csv(DATA_DIR / "products.csv")

        models["covisitation"].train(df_events)
        await models["covisitation"].save_model(DATA_DIR)

        # fixed merge bug args
        models["reranker"].train(df_events, df_users, df_products)
        await models["reranker"].save_model(DATA_DIR)

        models["sto"].train(df_events, df_users)
        await models["sto"].save_model(DATA_DIR)
        
    except Exception as e:
        print(f"Training failed: {e}")

@app.post("/api/train")
async def api_train(bg_tasks: BackgroundTasks):
    if not check_data():
        raise HTTPException(status_code=400, detail="Generate data first")
    bg_tasks.add_task(train_models_bg)
    return {"status": "started"}

@app.post("/api/predict")
async def predict_campaign(req: PersonaRequest):
    if not check_models():
        raise HTTPException(status_code=400, detail="Models not trained")

    # load if empty
    if not models["covisitation"].matrix:
        models["covisitation"].load_model(DATA_DIR)
        models["reranker"].load_model(DATA_DIR)
        models["sto"].load_model(DATA_DIR)

    df_users = pd.read_csv(DATA_DIR / "users.csv")
    df_products = pd.read_csv(DATA_DIR / "products.csv")

    # get a user matching the requested persona
    user_pool = df_users[df_users['persona'] == req.id]
    if user_pool.empty:
        raise HTTPException(status_code=404, detail="Persona not found in data")
        
    target_user = user_pool.sample(1).iloc[0].to_dict()
    
    seed_cat = target_user['preferred_category']
    seed_product_id = df_products[df_products['category'] == seed_cat]['product_id'].iloc[0]
    
    # Candidate Generation
    candidate_ids = models["covisitation"].get_candidates(seed_product_id, top_k=20)
    if not candidate_ids:
        candidate_ids = df_products[df_products['category'] == seed_cat]['product_id'].head(20).tolist()
        
    candidates_data = df_products[df_products['product_id'].isin(candidate_ids)].to_dict("records")
    
    # Reranking
    final_products = models["reranker"].rerank(candidates_data, target_user)[:5]

    # STO Predict
    optimal_hours = models["sto"].predict_optimal_hours(target_user)
    
    # NLG
    top_item = final_products[0] if len(final_products) > 0 else None
    headline = await models["headlines"].generate_headline(req.id, top_product=top_item)

    prod_txt = "\n".join([f"• {p['name']} - ₹{p['price']}" for p in final_products])
    msg = f"{headline}\n\n{prod_txt}\n\n⏰ Best time to send: {optimal_hours[0]}:00 IST"
    
    return {"message": msg, "user_id": target_user["user_id"]}