import os
import uvicorn
import asyncio
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

app = FastAPI(title="Meesho Micro-Moments")

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
    name: str
    description: str

def check_data():
    return (DATA_DIR / "events.csv").exists() and (DATA_DIR / "products.csv").exists()

def check_models():
    return (DATA_DIR / "sto_model.pkl").exists()


@app.get("/api/status")
def get_status():
    return {
        "data": check_data(),
        "model": check_models()
    }

@app.post("/api/generate-data")
async def generate_data(background_tasks: BackgroundTasks):
    async def task():
        print("🔄 Generating Data...")
        gen = DataGenerator(DATA_DIR)
        await gen.generate_all_data()
        print("✅ Data Generation Complete")
    
    background_tasks.add_task(task)
    return {"status": "started"}

@app.post("/api/train")
async def train(background_tasks: BackgroundTasks):
    if not check_data():
        raise HTTPException(400, "Data missing. Generate data first.")

    async def task():
        print("🔄 Training Models...")
        df_events = pd.read_csv(DATA_DIR / "events.csv")
        df_products = pd.read_csv(DATA_DIR / "products.csv")

        models["covisitation"].train(df_events)
        await models["covisitation"].save_model(DATA_DIR)

        models["sto"].train(df_events)
        await models["sto"].save_model(DATA_DIR)

        models["reranker"].train(df_events, df_products)
        await models["reranker"].save_model(DATA_DIR)

        models["headlines"].train(df_events)
        
        print("✅ Training Complete")

    background_tasks.add_task(task)
    return {"status": "started"}

@app.post("/api/predict")
async def predict(req: PersonaRequest):
    if not check_models():
        raise HTTPException(400, "Models not trained.")

    # 1. Load Data
    df_products = pd.read_csv(DATA_DIR / "products.csv")
    
    seeds = {
        "tier2_fashion": "fashion_ethnic",
        "student_examprep": "stationery",
        "budget_gadget": "electronics_budget", 
        "home_decor_festive": "home_decor_festive"
    }
    category = seeds.get(req.id, "fashion_ethnic")
    
    candidates = df_products[df_products["category"] == category].head(15).to_dict("records")
    if not candidates:
        candidates = df_products.head(10).to_dict("records")

    final_products = models["reranker"].rerank(candidates, category)[:5]

    hours = models["sto"].predict_optimal_hours(req.id)

    headline = await models["headlines"].generate_headline(req.dict())

    prod_txt = "\n".join([f"• {p['name']} - ₹{p['price']}" for p in final_products])
    msg = f"{headline}\n\n{prod_txt}\n\n⏰ Best time to send: {hours[0]}:00 IST"

    return {
        "headline": headline,
        "optimal_hours": hours,
        "products": [{"title": p["name"], "price": p["price"]} for p in final_products],
        "whatsapp_message": msg
    }

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)