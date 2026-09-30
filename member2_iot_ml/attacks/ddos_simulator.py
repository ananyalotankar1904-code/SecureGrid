from .attack_simulator import simulate_attack

def run_ddos(simulator, device_id, duration=10):
    """Triggers a network anomaly / DDoS attack behavior."""
    simulate_attack(simulator, device_id, "network_anomaly", duration)
