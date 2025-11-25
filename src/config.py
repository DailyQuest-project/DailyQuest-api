"""Configuration module for DailyQuest API.

This module loads environment variables and provides configuration settings
for the application including JWT settings, database configuration, and debug options.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS512"  # Padronizado com o auth service
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost/dailyquest"
)

# Auth Service Configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://dailyquest-auth-api:8080")

# Other configurations
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Testing Configuration
TESTING = os.getenv("TESTING", "False").lower() == "true"
