import threading
import time
import sys
from simulator.device_simulator import DeviceSimulator
from attacks.ddos_simulator import run_ddos
from simulator.config import DEFAULT_DEVICE_ID

def main():
    # Instantiate the existing simulator
    sim = DeviceSimulator(["meter_02", "meter_03", "meter_07"])
    
    # Run the simulator in a background daemon thread so we can script the attack
    print("Starting simulator thread...")
    t = threading.Thread(target=sim.run, daemon=True)
    t.start()
    
    # Wait for normal connection and a few normal packets
    time.sleep(3)
    
    print("\n--- INITIATING DDOS SIMULATION ---")
    # Trigger the DDoS attack using the existing simulator logic
    run_ddos(sim, "meter_07", duration=15)
    
    print("Attack complete. Waiting 2 seconds for any remaining normal packets...")
    time.sleep(2)
    print("Exiting trigger script.")
    sys.exit(0)

if __name__ == "__main__":
    main()
