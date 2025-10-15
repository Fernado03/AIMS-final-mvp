# services/speech_service.py
# OpenAI Whisper implementation for local speech-to-text transcription

import whisper
import tempfile
import os
import traceback
from pathlib import Path
from backend.config import WHISPER_MODEL, WHISPER_LANGUAGE

# Lazy load Whisper model to avoid loading it on import
_whisper_model = None
_model_name = WHISPER_MODEL  # Get from config

def get_whisper_model(model_name=None):
    """Lazy load Whisper model to save memory and startup time"""
    global _whisper_model, _model_name
    
    if model_name is None:
        model_name = WHISPER_MODEL
    
    if _whisper_model is None or _model_name != model_name:
        print(f"🎤 Loading Whisper '{model_name}' model... (this may take a moment on first run)")
        _whisper_model = whisper.load_model(model_name)
        _model_name = model_name
        print(f"✅ Whisper '{model_name}' model loaded successfully")
    
    return _whisper_model


def transcribe_audio_from_gcs(file_stream, original_filename):
    """
    Transcribe audio using OpenAI Whisper (local processing)
    
    Note: Function name kept for backward compatibility with existing routes.
    Now processes locally without Google Cloud Storage.
    
    Args:
        file_stream: File-like object containing audio data
        original_filename: Original filename (used to determine extension)
    
    Returns:
        str: Transcribed text
    """
    temp_file_path = None
    
    try:
        # Get file extension from original filename
        file_ext = Path(original_filename).suffix
        if not file_ext:
            file_ext = '.webm'  # Default to webm if no extension
        
        # Create temporary file with proper extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file_path = temp_file.name
            
            # Write uploaded file to temporary file
            file_stream.seek(0)
            file_data = file_stream.read()
            temp_file.write(file_data)
            temp_file.flush()
            
            file_size_mb = len(file_data) / (1024 * 1024)
            print(f"📝 Saved audio to temporary file: {temp_file_path} ({file_size_mb:.2f} MB)")
        
        # Auto-detect audio duration and choose model accordingly
        try:
            import librosa
            duration = librosa.get_duration(path=temp_file_path)
            print(f"⏱️ Audio duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            
            # Use faster model for long files
            if duration > 120:  # More than 2 minutes
                print(f"⚡ File is long ({duration:.1f}s), using 'base' model for faster processing")
                model = get_whisper_model('base')
            else:
                model = get_whisper_model()  # Use config model for short files
        except ImportError:
            print("ℹ️ librosa not installed, using file size as proxy for duration")
            # Fallback: Use file size as proxy (rough estimate: 1MB ≈ 1 minute for compressed audio)
            if file_size_mb > 3:  # Likely > 2 minutes
                print(f"⚡ Large file ({file_size_mb:.1f}MB), using 'base' model for faster processing")
                model = get_whisper_model('base')
            else:
                model = get_whisper_model()  # Use config model
        except Exception as e:
            print(f"⚠️ Could not detect duration: {e}, using default model")
            model = get_whisper_model()
        
        # Transcribe audio
        print(f"🎙️ Transcribing audio with Whisper...")
        result = model.transcribe(
            temp_file_path,
            language=WHISPER_LANGUAGE,  # From config
            task="transcribe",  # 'transcribe' or 'translate'
            fp16=False,  # Use FP32 for better compatibility on all systems
            verbose=False  # Reduce console spam for long files
        )
        
        transcript_text = result["text"].strip()
        print(f"✅ Whisper transcript: {transcript_text[:100]}..." if len(transcript_text) > 100 else f"✅ Whisper transcript: {transcript_text}")
        
        return transcript_text
    
    except Exception as e:
        print(f"❌ Error during Whisper transcription: {e}\n{traceback.format_exc()}")
        raise  # Re-raise to be caught by the route handler
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"🗑️ Deleted temporary audio file: {temp_file_path}")
            except Exception as e_del:
                print(f"⚠️ Warning: Could not delete temporary file {temp_file_path}: {e_del}")
