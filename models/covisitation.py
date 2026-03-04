import pandas as pd
from collections import defaultdict
import pickle

class CovisitationModel:
    def __init__(self):
        # Maps product_id ---> {related_product_id: count}
        self.matrix = defaultdict(lambda: defaultdict(int))

    def train(self, df_events):
        print("Training Co-visitation Matrix...")
        
        #  matrix approach
        sessions = df_events.groupby('session_id')['product_id'].apply(list)
        
        for items in sessions:
            unique_items = list(set(items))
            for i in range(len(unique_items)):
                for j in range(i + 1, len(unique_items)):
                    item_a, item_b = unique_items[i], unique_items[j]
                    self.matrix[item_a][item_b] += 1
                    self.matrix[item_b][item_a] += 1
                    
        # cast back to standard dict to avoid pickle issues with lambdas
        self.matrix = {k: dict(v) for k, v in self.matrix.items()}

    async def save_model(self, data_dir):
        with open(data_dir / "covisitation_model.pkl", "wb") as f:
            pickle.dump(self.matrix, f)

    def load_model(self, data_dir):
        path = data_dir / "covisitation_model.pkl"
        if path.exists():
            with open(path, "rb") as f:
                self.matrix = pickle.load(f)

    def get_candidates(self, seed_product_id, top_k=50):
        if seed_product_id not in self.matrix:
            return []
        # sort by freq
        sorted_items = sorted(self.matrix[seed_product_id].items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_items[:top_k]]