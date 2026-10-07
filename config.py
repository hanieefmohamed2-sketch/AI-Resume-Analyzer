"""
config.py

Centralized configuration: loads environment variables and defines
constants used across the project. Change values here, not scattered
across multiple files.
"""

import os
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

# Which AI provider to use: "openai" or "gemini"
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")

# API keys (kept out of source code)
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# Model names
OPENAI_MODEL: str = "gpt-4o-mini"
GEMINI_MODEL: str = "gemini-1.5-flash"

# File upload constraints
MAX_FILE_SIZE_MB: int = 5
ALLOWED_FILE_TYPES: list = ["pdf"]