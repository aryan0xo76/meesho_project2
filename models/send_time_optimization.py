import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class SendTimeOptimizer:
    def __init__(self):
        # rf handles the non-linear cyclical time better than logistic reg
        self.model = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
        self.personas = ["tier2_fashion", "student_examprep", "budget_gadget", "home_decor_festive"]

    def _encode_time(self, hour):
        return np.sin(2 * np.pi * hour / 24.0), np.cos(2 * np.pi * hour / 24.0)

    def train(self, df_events, df_users):
        print("Training User-Level STO Model...")
        df = df_events.merge(df_users[['user_id', 'persona', 'past_30d_spend', 'base_shopping_hour']], on='user_id')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour_of_day'] = df['timestamp'].dt.hour
        
        df['is_engaged'] = df['event_type'].isin(['cart', 'purchase']).astype(int)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24.0)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24.0)
        
        # convert persona to int
        df['persona_idx'] = df['persona'].apply(lambda x: self.personas.index(x) if x in self.personas else 0)
        
        features = ['hour_sin', 'hour_cos', 'persona_idx', 'past_30d_spend', 'base_shopping_hour']
        
        # balance classes a bit 
        engaged = df[df['is_engaged'] == 1]
        not_engaged = df[df['is_engaged'] == 0].sample(n=len(engaged), random_state=42)
        balanced_df = pd.concat([engaged, not_engaged])
        
        self.model.fit(balanced_df[features], balanced_df['is_engaged'])

    async def save_model(self, data_dir):
        with open(data_dir / "sto_model.pkl", "wb") as f:
            pickle.dump(self.model, f)

    def load_model(self, data_dir):
        path = data_dir / "sto_model.pkl"
        if path.exists():
            with open(path, "rb") as f:
                self.model = pickle.load(f)

    def predict_optimal_hours(self, user_profile, top_k=3):
        persona_id = user_profile.get("persona", "default")
        p_idx = self.personas.index(persona_id) if persona_id in self.personas else 0
        spend = user_profile.get("past_30d_spend", 1000)
        base_hour = user_profile.get("base_shopping_hour", 12)

        hours = np.arange(24)
        sin_time, cos_time = self._encode_time(hours)
        
        X_test = pd.DataFrame({
            'hour_sin': sin_time,
            'hour_cos': cos_time,
            'persona_idx': p_idx,
            'past_30d_spend': spend,
            'base_shopping_hour': base_hour
        })
        
        probs = self.model.predict_proba(X_test)[:, 1]
        best_hours = hours[np.argsort(probs)[::-1]][:top_k]
        return best_hours