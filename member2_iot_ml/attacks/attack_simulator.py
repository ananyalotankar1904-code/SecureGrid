from simulator.device_simulator import DeviceSimulator
import time

def simulate_attack(simulator: DeviceSimulator, device_id: str, attack_type: str, duration: int):
    """
    Simulates a specific attack for a given duration (in seconds), then returns to normal.
    This modifies the running simulator's state.
    """
    print(f"--- Starting Attack: {attack_type} on {device_id} for {duration}s ---")
    simulator.set_mode(device_id, attack_type)
    
    if duration > 0:
        time.sleep(duration)
        print(f"--- Ending Attack on {device_id}, returning to normal ---")
        simulator.set_mode(device_id, "normal")
