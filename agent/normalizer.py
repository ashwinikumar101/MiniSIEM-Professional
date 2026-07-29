# ==========================================
# MiniSIEM Agent
# Event Normalizer
# ==========================================

def normalize(data):

    return {

        "timestamp": data.get("timestamp"),

        "event": data.get("event"),

        "username": data.get("username"),

        "ip": data.get("ip"),

        "computer": data.get("computer"),

        "provider": data.get("provider"),

        "severity": "LOW",

        "source": "Windows",

        "category": "Authentication"

    }