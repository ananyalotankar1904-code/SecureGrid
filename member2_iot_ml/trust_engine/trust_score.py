from .trust_config import WEIGHTS, THRESHOLDS

def calculate_trust_score(anomaly_result: dict, base_trust: int = 100) -> dict:
    """
    Calculates a dynamic trust score (0-100) based on the latest anomaly analysis.
    This does NOT execute any quarantine logic; it only assesses trust.
    """
    if "error" in anomaly_result:
        return {"error": anomaly_result["error"]}
        
    score = base_trust * WEIGHTS["history"]
    reasons = []
    
    # 1. Energy behavior (30%)
    if not anomaly_result.get("energy_anomaly"):
        score += 100 * WEIGHTS["energy_behavior"]
    else:
        reasons.append("abnormal energy consumption")
        
    # 2. Network behavior (40%)
    if not anomaly_result.get("network_anomaly"):
        score += 100 * WEIGHTS["device_behavior"]
    else:
        reasons.append("abnormally high request rate")
        
    # 3. Security behavior (20%)
    if not anomaly_result.get("failed_auth_anomaly"):
        score += 100 * WEIGHTS["security_behavior"]
    else:
        reasons.append("authentication failures detected")
        
    final_score = int(score)
    
    # Determine trust status
    if final_score >= THRESHOLDS["TRUSTED"]:
        status = "TRUSTED"
    elif final_score >= THRESHOLDS["SUSPICIOUS"]:
        status = "SUSPICIOUS"
    else:
        status = "HIGH_RISK"
        
    return {
        "device_id": anomaly_result.get("device_id"),
        "trust_score": final_score,
        "trust_status": status,
        "reasons": reasons
    }
