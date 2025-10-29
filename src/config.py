"""Configuration module for DailyQuest API.

This module loads environment variables and provides configuration settings
for the application including JWT settings, database configuration, and debug options.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost/dailyquest"
)

# Other configurations
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
