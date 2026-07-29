# ==========================================
# Windows Security Event IDs
# SecureVision SIEM
# ==========================================

EVENT_IDS = {

    # Authentication
    4624: "LOGIN_SUCCESS",
    4625: "LOGIN_FAILED",
    4634: "LOGOFF",

    # Account Management
    4720: "USER_CREATED",
    4722: "USER_ENABLED",
    4725: "USER_DISABLED",
    4726: "USER_DELETED",
    4738: "USER_MODIFIED",
    4740: "ACCOUNT_LOCKED",

    # Password Events
    4723: "PASSWORD_CHANGE",
    4724: "PASSWORD_RESET",

    # Group Management
    4732: "USER_ADDED_TO_GROUP",
    4733: "USER_REMOVED_FROM_GROUP",

    # Service Events
    7036: "SERVICE_STARTED",
    7035: "SERVICE_CONTROL",

    # Firewall
    5152: "FIREWALL_BLOCKED",
    5156: "FIREWALL_ALLOWED",

    # Windows Defender (commonly seen IDs)
    1116: "DEFENDER_MALWARE_DETECTED",
    1117: "DEFENDER_ACTION_TAKEN"
}