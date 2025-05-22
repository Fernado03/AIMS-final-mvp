import os

# Google Cloud Storage
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]

# Vertex AI and Gemini Model
VERTEX_AI_PROJECT_ID = os.environ["VERTEX_AI_PROJECT_ID"]
VERTEX_AI_LOCATION = os.environ["VERTEX_AI_LOCATION"]
VERTEX_AI_MODEL_NAME = os.environ["VERTEX_AI_MODEL_NAME"]

# Speech Service
SPEECH_LANGUAGE_CODE = os.environ["SPEECH_LANGUAGE_CODE"]
SPEECH_MODEL = os.environ["SPEECH_MODEL"]
SPEECH_ENABLE_AUTOMATIC_PUNCTUATION = os.environ["SPEECH_ENABLE_AUTOMATIC_PUNCTUATION"].lower() in ('true', '1', 't', 'y', 'yes')

# Database
DATABASE_NAME = os.environ["DATABASE_NAME"]
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_NAME)