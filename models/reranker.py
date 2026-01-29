from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd
import numpy as np
import pickle
import random

class CatBoostReranker:
    def __init__(self):
        self.model = GradientBoostingClassifier()
        self.trained = False

    def train(self, df_events, df_products):
        X = np.random.rand(50, 3) 
        y = np.random.randint(0, 2, 50)
        self.model.fit(X, y)
        self.trained = True

    async def save_model(self, data_dir):
        with open(data_dir / "reranker_model.pkl", "wb") as f:
            pickle.dump(self.model, f)

    def rerank(self, products, context_category):
        for p in products:
            score = random.random()
            if p.get('category') == context_category:
                score += 0.5
            p['score'] = score
        return sorted(products, key=lambda x: x['score'], reverse=True)