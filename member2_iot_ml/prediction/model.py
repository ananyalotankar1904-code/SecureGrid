import numpy as np

class EWMAModel:
    """
    Exponentially Weighted Moving Average (EWMA) for load forecasting.
    This provides a genuine, lightweight statistical prediction suitable for a prototype.
    It doesn't require a large dataset and works smoothly in real-time.
    """
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.history = {}

    def predict(self, device_id: str, current_power: float) -> float:
        if device_id not in self.history:
            self.history[device_id] = current_power
            return round(current_power, 2)
        
        # Calculate EWMA
        prev_ema = self.history[device_id]
        new_ema = self.alpha * current_power + (1 - self.alpha) * prev_ema
        self.history[device_id] = new_ema
        
        return round(new_ema, 2)

# Global instance for stateful prediction in prototype
_model = EWMAModel()

def simple_predict(device_id: str, current_power: float) -> float:
    return _model.predict(device_id, current_power)
