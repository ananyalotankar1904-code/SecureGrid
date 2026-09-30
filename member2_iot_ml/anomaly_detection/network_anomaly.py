def detect_network_anomaly(request_rate: int, failed_auth: int, max_rate: int = 50, max_auth_fails: int = 3) -> dict:
    """
    Detects network-based anomalies, such as DDoS-like request rates 
    or repetitive authentication failures.
    """
    net_anomaly = request_rate > max_rate
    auth_anomaly = failed_auth > max_auth_fails
    
    is_anomaly = net_anomaly or auth_anomaly
    reasons = []
    score = 0
    
    if net_anomaly:
        reasons.append("abnormally high request rate")
        score += min(50, int(request_rate / 10))
        
    if auth_anomaly:
        reasons.append("authentication failures detected")
        score += min(50, failed_auth * 10)
        
    return {
        "is_anomaly": is_anomaly,
        "score": min(100, score),
        "reasons": reasons
    }
