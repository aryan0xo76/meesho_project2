import pickle

class SendTimeOptimizer:
    def __init__(self):
        self.patterns = {}

    def train(self, df_events):
        self.patterns = {
            "tier2_fashion": [14, 15, 16],
            "student_examprep": [22, 23, 0],
            "budget_gadget": [19, 20, 21],
            "home_decor_festive": [10, 11, 12]
        }

    async def save_model(self, data_dir):
        with open(data_dir / "sto_model.pkl", "wb") as f:
            pickle.dump(self.patterns, f)

    def predict_optimal_hours(self, persona_id):
        return self.patterns.get(persona_id, [10, 11, 12])