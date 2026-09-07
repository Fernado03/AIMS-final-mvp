import whisper
import tempfile
import os
import traceback
from pathlib import Path
from backend.config import WHISPER_MODEL, WHISPER_LANGUAGE

_whisper_model = None
_model_name = WHISPER_MODEL


def get_whisper_model(model_name=None):
    global _whisper_model, _model_name
    if model_name is None:
        model_name = WHISPER_MODEL
    if _whisper_model is None or _model_name != model_name:
        print(f"🎤 Loading Whisper '{model_name}' model... (this may take a moment on first run)")
        _whisper_model = whisper.load_model(model_name)
        _model_name = model_name
        print(f"✅ Whisper '{model_name}' model loaded successfully")
    return _whisper_model


def transcribe_audio(file_stream, original_filename):
    temp_file_path = None
    try:
        file_ext = Path(original_filename).suffix or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file_path = temp_file.name
            file_stream.seek(0)
            file_data = file_stream.read()
            temp_file.write(file_data)
            temp_file.flush()
            file_size_mb = len(file_data) / (1024 * 1024)
            print(f"📝 Saved audio to temporary file: {temp_file_path} ({file_size_mb:.2f} MB)")
        # ponytail: filesize proxy instead of librosa duration; swap if duration-based model pick matters
        model = get_whisper_model("base") if file_size_mb > 3 else get_whisper_model()
        print("🎙️ Transcribing audio with Whisper...")
        result = model.transcribe(
            temp_file_path,
            language=WHISPER_LANGUAGE,
            task="transcribe",
            fp16=False,
            verbose=False,
        )
        transcript_text = result["text"].strip()
        print(f"✅ Whisper transcript: {transcript_text[:100]}{'...' if len(transcript_text) > 100 else ''}")
        return transcript_text
    except Exception as e:
        print(f"❌ Error during Whisper transcription: {e}\n{traceback.format_exc()}")
        raise
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e_del:
                print(f"⚠️ Warning: Could not delete temporary file {temp_file_path}: {e_del}")
