from .attack_simulator import simulate_attack

def run_compromised(simulator, device_id, duration=10):
    """Triggers a compromised device scenario (energy + network anomaly)."""
    simulate_attack(simulator, device_id, "compromised", duration)
