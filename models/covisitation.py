import pickle

class CovisitationModel:
    def __init__(self):
        self.matrix = {}

    def train(self, df_events):
        self.matrix = {"status": "trained"}

    async def save_model(self, data_dir):
        with open(data_dir / "covisitation_model.pkl", "wb") as f:
            pickle.dump(self.matrix, f)