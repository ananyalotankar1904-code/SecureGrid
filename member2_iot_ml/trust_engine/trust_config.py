# Prototype weightings for trust score calculation
WEIGHTS = {
    "device_behavior": 0.40,  # Based on network request rates
    "energy_behavior": 0.30,  # Based on power consumption
    "security_behavior": 0.20,  # Based on authentication failures
    "history": 0.10             # Baseline trust derived from history (mocked here)
}

# Trust thresholds
THRESHOLDS = {
    "TRUSTED": 85,
    "SUSPICIOUS": 50,
    # Below 50 is HIGH_RISK
}
