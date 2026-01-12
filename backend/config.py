import os

# Google Generative AI (Gemini) Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-3-flash-preview")

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "aims_medical_scribe")
# DATABASE_PATH removed as it is not needed for MongoDB

# Whisper Speech-to-Text Configuration (Local processing)
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "medium")  # Options: tiny, base, small, medium, large
WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "en")  # Language code for transcription


