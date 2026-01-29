import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import asyncio

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
        """Main Orchestrator"""
        await self.generate_users()
        await self.generate_products()
        await self.generate_smart_interactions()

    async def generate_users(self, n=500):
        users = []
        personas = ["tier2_fashion", "student_examprep", "budget_gadget", "home_decor_festive"]
        for i in range(n):
            users.append({
                "user_id": f"U{str(i).zfill(4)}",
                "name": fake.name(),
                "city": fake.city(),
                "persona": random.choice(personas)
            })
        pd.DataFrame(users).to_csv(self.data_dir / "users.csv", index=False)

    async def generate_products(self, n=200):
        products = []
        adjectives = ["Premium", "Budget", "Designer", "Handmade", "Imported", "Classic"]
        
        for i in range(n):
            cat = random.choice(list(self.categories.keys()))
            base_name = random.choice(self.categories[cat])
            adj = random.choice(adjectives)
            products.append({
                "product_id": f"P{str(i).zfill(4)}",
                "name": f"{adj} {base_name}",
                "category": cat,
                "price": random.randint(150, 2500)
            })
        pd.DataFrame(products).to_csv(self.data_dir / "products.csv", index=False)

    async def generate_smart_interactions(self, n_events=5000):
        """
        Generates events with 'Hidden Logic' for the AI to find.
        - Students buy at night.
        - Fashion shoppers buy in afternoon.
        - Festivals trigger Home Decor.
        """
        users = pd.read_csv(self.data_dir / "users.csv").to_dict('records')
        products = pd.read_csv(self.data_dir / "products.csv").to_dict('records')
        
        events = []
        start_date = datetime.now() - timedelta(days=90)
        
        for _ in range(n_events):
            user = random.choice(users)
            
            if user["persona"] == "student_examprep":
                hour = random.choice([21, 22, 23, 0]) 
            elif user["persona"] == "home_decor_festive":
                hour = random.choice([10, 11, 12]) 
            else:
                hour = random.randint(9, 21)
                
            ts = start_date + timedelta(days=random.randint(0, 90), hours=hour)
            
            if random.random() < 0.7:
                mapping = {
                    "tier2_fashion": "fashion_ethnic",
                    "student_examprep": "stationery",
                    "budget_gadget": "electronics_budget",
                    "home_decor_festive": "home_decor_festive"
                }
                pref_cat = mapping.get(user["persona"])
                subset = [p for p in products if p["category"] == pref_cat]
                product = random.choice(subset) if subset else random.choice(products)
            else:
                product = random.choice(products)
            
            events.append({
                "user_id": user["user_id"],
                "product_id": product["product_id"],
                "category": product["category"],
                "event_type": random.choice(["view", "cart", "purchase"]),
                "timestamp": ts,
                "day_of_week": ts.strftime("%A")
            })
            
        pd.DataFrame(events).to_csv(self.data_dir / "events.csv", index=False)