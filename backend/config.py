import os
from dotenv import load_dotenv

load_dotenv()
# OpenAI-compatible LLM (hcnsec)
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.hcnsec.cn/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "step-explore")

# MongoDB Configuration (local Docker by default)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "aims_medical_scribe")

# Whisper Speech-to-Text Configuration (Local processing)
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "medium")  # Options: tiny, base, small, medium, large
WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "en")  # Language code for transcription
