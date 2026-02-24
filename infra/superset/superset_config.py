"""
Superset Configuration for AdventureWorks Analytics

This configuration sets up Superset to connect to Polaris/Iceberg
for analytics dashboarding.
"""

import os
from datetime import timedelta

# Superset Secret Key
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "thisismysecretkey123456789")

# Database Configuration - Polaris/Iceberg via Trino
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SUPERSET_DATABASE_URI",
    "postgresql://superset:superset@superset-db:5432/superset"
)

# Enable SQLAlchemy features
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ALERT_REPORTS": True,
    "ENABLE_CHUNKING": True,
}

# Cache Configuration
CACHE_DEFAULT_TIMEOUT = 60 * 60 * 24  # 1 day

# Timezone
SUPERSET_WEBSERVER_TIMEOUT = 60
SUPERSET_WEBSERVER_WORKERS = 4

# Dashboard Configuration
DEFAULT_VIZ_TYPE = "dist_bar"

# Email Configuration (optional - for alerts)
EMAIL_NOTIFICATIONS = True

# API Configuration
ENABLE_PROXY_FIX = True
WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = []

# Row Level Security
SUPERSET_AUTH_TYPE = "flask_appbuilder.security.manager.db"

# Logging
LOG_LEVEL = "INFO"

# Custom CSS/JS
SUPERSET_WEBSERVER_PORT = 8088

# Database connections (for Iceberg)
ADDITIONAL_DATABASES = [
    {
        "name": "AdventureWorks Iceberg",
        "sqlalchemy_uri": "trino://trino@trino:8080/iceberg",
        "extra": {
            "cache_timeout": 3600,
            "allows_virtual_table_explore": True,
        }
    }
]

# Dashboard export/import settings
ENABLE_CSV_EXPORT = True
EXCEL_EXPORT = True

# Security
SUPERSET_BANNER = "AdventureWorks Analytics"
SUPERSET_BANNER_ICON = "/static/assets/images/superset-logo.png"

# Celery configuration (for async queries)
CELERY_CONFIG = "superset.tasks.celery_app:app"

# Timezone
SUPERSET_TIMEZONE = "Asia/Singapore"
