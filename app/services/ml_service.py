import random

class MLService:
    async def predict(self, image_path: str):
        # Mock inference
        labels = ["Apple", "Banana", "Carrot", "Tomato"]
        return {
            "label": random.choice(labels),
            "confidence": random.uniform(0.8, 0.99),
            "contamination_score": random.uniform(0.0, 0.1)
        }

ml_service = MLService()
