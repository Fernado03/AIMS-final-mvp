import os

# Vertex AI and Gemini Model (for LLM generation)
VERTEX_AI_PROJECT_ID = os.environ.get("VERTEX_AI_PROJECT_ID", "")
VERTEX_AI_LOCATION = os.environ.get("VERTEX_AI_LOCATION", "us-central1")
VERTEX_AI_MODEL_NAME = os.environ.get("VERTEX_AI_MODEL_NAME", "gemini-2.5-flash-lite")

# Whisper Speech-to-Text Configuration (Local processing)
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "medium")  # Options: tiny, base, small, medium, large
WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "en")  # Language code for transcription

# Database
DATABASE_NAME = os.environ.get("DATABASE_NAME", "notes_main.db")
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_NAME)
