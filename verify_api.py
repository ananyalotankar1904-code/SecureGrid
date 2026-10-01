import requests

def verify():
    devs = requests.get("http://localhost:8000/devices").json()
    preds = requests.get("http://localhost:8000/predictions").json()
    tels = requests.get("http://localhost:8000/telemetry").json()
    evts = requests.get("http://localhost:8000/security/events").json()
    
    print("Devices:", devs)
    print("Predictions:", preds)
    print("Telemetry:", tels)
    print("Events:", evts)

if __name__ == "__main__":
    verify()
