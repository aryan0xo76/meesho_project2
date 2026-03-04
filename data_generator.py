import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import os

fake = Faker('en_IN')

class DataGenerator:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.categories = {
            "fashion_ethnic": ["Silk Saree", "Kurta Set", "Lehenga", "Dupatta", "Sherwani"],
            "electronics_budget": ["Earbuds", "Smart Watch", "Power Bank", "Data Cable", "Phone Case"],
            "home_decor_festive": ["Diya Set", "Rangoli Stencil", "String Lights", "Toran", "Cushion Covers"],
            "stationery": ["Notebook Set", "Gel Pens", "Geometry Box", "Exam Pad", "Calculator"]
        }
        
    async def generate_all_data(self):
        print("Generating mock DB...")
        users = await self.generate_users()
        products = await self.generate_products()
        await self.generate_smart_interactions(users, products)
        print("Done.")

    async def generate_users(self, n=500):
        users = []
        personas = ["tier2_fashion", "student_examprep", "budget_gadget", "home_decor_festive"]
        
        # map personas to categories
        pref_mapping = {
            "tier2_fashion": "fashion_ethnic",
            "student_examprep": "stationery",
            "budget_gadget": "electronics_budget",
            "home_decor_festive": "home_decor_festive"
        }
        
        for i in range(n):
            persona = random.choice(personas)
            users.append({
                "user_id": f"U{i}",
                "persona": persona,
                "preferred_category": pref_mapping[persona],
                "past_30d_spend": round(random.uniform(100, 5000), 2),
                "base_shopping_hour": random.randint(8, 23)
            })
            
        df = pd.DataFrame(users)
        df.to_csv(self.data_dir / "users.csv", index=False)
        return users

    async def generate_products(self):
        products = []
        p_id = 0
        for cat, items in self.categories.items():
            for item in items:
                # generate 5 variations per item to bulk up the catalog
                for _ in range(5):
                    products.append({
                        "product_id": f"P{p_id}",
                        "name": f"{fake.word().capitalize()} {item}",
                        "category": cat,
                        "price": round(random.uniform(99, 1999), 2)
                    })
                    p_id += 1
                    
        df = pd.DataFrame(products)
        df.to_csv(self.data_dir / "products.csv", index=False)
        return products

    async def generate_smart_interactions(self, users, products, target_events=50000):
        events = []
        session_id_counter = 1000
        
        # cache for speed
        cat_products = {cat: [p for p in products if p['category'] == cat] for cat in self.categories.keys()}
        
        while len(events) < target_events:
            user = random.choice(users)
            
            # user's usual shopping time +/- a bit of noise
            event_hour = max(0, min(23, int(np.random.normal(user["base_shopping_hour"], 2))))
            base_ts = datetime.now() - timedelta(days=random.randint(0, 30))
            base_ts = base_ts.replace(hour=event_hour, minute=random.randint(0, 59))
            
            session_length = random.randint(1, 4)
            session_id = f"S{session_id_counter}"
            session_id_counter += 1
            
            # 70% chance they shop in their preferred category
            session_cat = user["preferred_category"] if random.random() < 0.7 else random.choice(list(self.categories.keys()))
            available_prods = cat_products.get(session_cat, products)
            
            for _ in range(session_length):
                product = random.choice(available_prods)
                rand_val = random.random()
                
                # simulate funnel dropout
                if rand_val < 0.05: event_type = "purchase"
                elif rand_val < 0.15: event_type = "cart"
                else: event_type = "view"
                
                events.append({
                    "user_id": user["user_id"],
                    "session_id": session_id,
                    "product_id": product["product_id"],
                    "event_type": event_type,
                    "timestamp": base_ts.strftime("%Y-%m-%d %H:%M:%S")
                })
                base_ts += timedelta(minutes=random.randint(1, 5))
                
        df = pd.DataFrame(events)
        df.to_csv(self.data_dir / "events.csv", index=False)