import json
from simulator.telemetry_generator import generate_telemetry
from anomaly_detection.anomaly_engine import analyze_telemetry
from trust_engine.trust_score import calculate_trust_score
from trust_engine.security_event import generate_security_event
from prediction.load_prediction import predict_load

def print_result(title, telemetry, analysis, trust, event):
    print(f"\n{'='*40}")
    print(f"--- {title} ---")
    print("Telemetry:")
    print(json.dumps(telemetry, indent=2))
    print("Analysis:")
    print(json.dumps(analysis, indent=2))
    print("Trust Result:")
    print(json.dumps(trust, indent=2))
    print("Security Event:")
    print(json.dumps(event, indent=2))

def test_flow():
    print("=== END TO END PIPELINE TESTS ===")
    
    device_id = "meter_test_01"
    
    # 1. Normal
    tel_norm = generate_telemetry(device_id, "normal", seed=42)
    an_norm = analyze_telemetry(tel_norm)
    tr_norm = calculate_trust_score(an_norm)
    ev_norm = generate_security_event(tel_norm, an_norm, tr_norm)
    pred_norm = predict_load(tel_norm)
    print_result("NORMAL MODE", tel_norm, an_norm, tr_norm, ev_norm)
    print("Prediction:", json.dumps(pred_norm, indent=2))
    
    # 2. Attack / Compromised
    tel_att = generate_telemetry(device_id, "compromised", seed=43)
    an_att = analyze_telemetry(tel_att)
    tr_att = calculate_trust_score(an_att)
    ev_att = generate_security_event(tel_att, an_att, tr_att)
    print_result("ATTACK MODE (COMPROMISED)", tel_att, an_att, tr_att, ev_att)

    # 3. Energy Only (False positive check)
    tel_energy = generate_telemetry(device_id, "energy_anomaly", seed=44)
    an_energy = analyze_telemetry(tel_energy)
    tr_energy = calculate_trust_score(an_energy)
    ev_energy = generate_security_event(tel_energy, an_energy, tr_energy)
    print_result("ENERGY ANOMALY ONLY (FALSE POSITIVE CHECK)", tel_energy, an_energy, tr_energy, ev_energy)
    
    # 4. Network Only
    tel_net = generate_telemetry(device_id, "network_anomaly", seed=45)
    an_net = analyze_telemetry(tel_net)
    tr_net = calculate_trust_score(an_net)
    ev_net = generate_security_event(tel_net, an_net, tr_net)
    print_result("NETWORK ANOMALY ONLY", tel_net, an_net, tr_net, ev_net)

    # 5. Malformed Telemetry
    tel_bad = {"device_id": device_id, "power_kw": "not_a_number"}
    an_bad = analyze_telemetry(tel_bad)
    tr_bad = calculate_trust_score(an_bad)
    if "error" in an_bad:
        ev_bad = {"error": "Cannot generate event due to previous errors."}
    else:
        ev_bad = generate_security_event(tel_bad, an_bad, tr_bad)
    print_result("MALFORMED TELEMETRY", tel_bad, an_bad, tr_bad, ev_bad)

if __name__ == "__main__":
    test_flow()
