from catboost import CatBoostRanker, Pool
import pandas as pd
import pickle

class CatBoostReranker:
    def __init__(self):
        # using YetiRank for ndcg optimization 
        self.model = CatBoostRanker(
            iterations=100, 
            depth=4, 
            learning_rate=0.1, 
            loss_function='YetiRank', 
            verbose=False
        )
        self.item_stats = {}

    def _engineer_features(self, df_events):
        stats = df_events.groupby('product_id').agg(
            total_interactions=('event_type', 'count'),
            purchases=('event_type', lambda x: (x == 'purchase').sum()),
            carts=('event_type', lambda x: (x == 'cart').sum())
        ).reset_index()
        
        # simple smoothing so we don't divide by zero
        stats['historical_cvr'] = stats['purchases'] / (stats['total_interactions'] + 1)
        stats['historical_ctr'] = (stats['carts'] + stats['purchases']) / (stats['total_interactions'] + 1)
        return stats.set_index('product_id').to_dict('index')

    def train(self, df_events, df_users, df_products):
        print("Training Reranker...")
        self.item_stats = self._engineer_features(df_events)
        
        df = df_events.merge(df_users, on='user_id').merge(df_products, on='product_id')
        
        relevance_map = {'view': 1, 'cart': 2, 'purchase': 3}
        df['relevance'] = df['event_type'].map(relevance_map)
        
        df['historical_cvr'] = df['product_id'].map(lambda x: self.item_stats.get(x, {}).get('historical_cvr', 0))
        df['historical_ctr'] = df['product_id'].map(lambda x: self.item_stats.get(x, {}).get('historical_ctr', 0))
        df['is_preferred_category'] = (df['category'] == df['preferred_category']).astype(int)
        
        # MUST sort by user_id for CatBoost YetiRank grouping
        df = df.sort_values('user_id').reset_index(drop=True)
        
        features = ['price', 'past_30d_spend', 'historical_cvr', 'historical_ctr', 'is_preferred_category']
        train_pool = Pool(data=df[features], label=df['relevance'], group_id=df['user_id'])
        
        self.model.fit(train_pool)

    async def save_model(self, data_dir):
        self.model.save_model(str(data_dir / "catboost_reranker.cbm"))
        with open(data_dir / "item_stats.pkl", "wb") as f:
            pickle.dump(self.item_stats, f)

    def load_model(self, data_dir):
        self.model.load_model(str(data_dir / "catboost_reranker.cbm"))
        path = data_dir / "item_stats.pkl"
        if path.exists():
            with open(path, "rb") as f:
                self.item_stats = pickle.load(f)

    def rerank(self, candidate_products, user_profile):
        if not candidate_products: return []
        
        df_candidates = pd.DataFrame(candidate_products)
        df_candidates['past_30d_spend'] = user_profile.get('past_30d_spend', 0)
        df_candidates['historical_cvr'] = df_candidates['product_id'].map(lambda x: self.item_stats.get(x, {}).get('historical_cvr', 0))
        df_candidates['historical_ctr'] = df_candidates['product_id'].map(lambda x: self.item_stats.get(x, {}).get('historical_ctr', 0))
        df_candidates['is_preferred_category'] = (df_candidates['category'] == user_profile.get('preferred_category', '')).astype(int)
        
        features = ['price', 'past_30d_spend', 'historical_cvr', 'historical_ctr', 'is_preferred_category']
        
        # predict() returns raw score
        df_candidates['score'] = self.model.predict(df_candidates[features])
        
        return df_candidates.sort_values(by='score', ascending=False).to_dict('records')