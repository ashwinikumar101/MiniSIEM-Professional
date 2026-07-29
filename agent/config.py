# ==========================================
# MiniSIEM Agent
# Configuration
# ==========================================

# Collector Settings
POLL_INTERVAL = 5          # Seconds
MAX_EVENTS = 100
MAX_QUEUE_SIZE = 1000

# Logging
LOG_LEVEL = "INFO"

# Database
DATABASE = "database/siem.db"

# Windows
WINDOWS_LOG = "Security"

# Collector
COLLECTOR_NAME = "MiniSIEM Agent"

COLLECTOR_VERSION = "2.0"

# Dashboard
ENABLE_LIVE_STATUS = True

# Queue
ENABLE_QUEUE = True

# Metrics
ENABLE_METRICS = True