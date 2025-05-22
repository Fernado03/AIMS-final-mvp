# services/speech_service.py

from google.cloud.speech_v2 import SpeechClient, BatchRecognizeRequest, BatchRecognizeFileMetadata
from google.cloud.speech_v2.types import RecognitionConfig, RecognizeRequest, RecognitionFeatures, RecognitionOutputConfig, InlineOutputConfig
from google.cloud import storage
import uuid
import traceback
from backend.config import (
    GCS_BUCKET_NAME,
    VERTEX_AI_PROJECT_ID,
    SPEECH_LANGUAGE_CODE,
    SPEECH_MODEL,
    SPEECH_ENABLE_AUTOMATIC_PUNCTUATION
) # Import from config

speech_client = SpeechClient()
storage_client = storage.Client()

def transcribe_audio_from_gcs(file_stream, original_filename):
    gcs_uri = None
    blob_name = None
    try:
        blob_name = f"audio_uploads/{uuid.uuid4()}-{original_filename}"
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(blob_name)

        file_stream.seek(0)
        blob.upload_from_file(file_stream)

        gcs_uri = f"gs://{GCS_BUCKET_NAME}/{blob_name}"
        print(f"Uploaded audio to GCS: {gcs_uri}")

        project_id = VERTEX_AI_PROJECT_ID
        recognizer_path = f"projects/{project_id}/locations/global/recognizers/_" # Using '_' for default recognizer

        speech_features = RecognitionFeatures(enable_automatic_punctuation=SPEECH_ENABLE_AUTOMATIC_PUNCTUATION)
        speech_config = RecognitionConfig(
            features=speech_features,
            language_codes=[SPEECH_LANGUAGE_CODE],
            model=SPEECH_MODEL, # Ensure this model name is correct for v2 and your project
            auto_decoding_config={}
        )

        inline_cfg = InlineOutputConfig()
        output_config = RecognitionOutputConfig(inline_response_config=inline_cfg)

        request_payload = BatchRecognizeRequest(
            recognizer=recognizer_path,
            config=speech_config,
            files=[BatchRecognizeFileMetadata(uri=gcs_uri)],
            recognition_output_config=output_config
        )

        operation = speech_client.batch_recognize(request=request_payload)
        response = operation.result(timeout=600)

        full_transcript = []
        for file_result in response.results.values():
            inline = file_result.inline_result
            for segment in inline.transcript.results:
                if segment.alternatives:
                    alt = segment.alternatives[0]
                    full_transcript.append(alt.transcript)

        transcript_text = " ".join(full_transcript).strip()
        print(f"📝 Google STT transcript: {transcript_text}")
        return transcript_text

    except Exception as e:
        print(f"Error during transcription: {e}\n{traceback.format_exc()}")
        raise # Re-raise to be caught by the route handler
    finally:
        if gcs_uri and blob_name:
            try:
                bucket = storage_client.bucket(GCS_BUCKET_NAME)
                blob = bucket.blob(blob_name)
                blob.delete()
                print(f"Deleted GCS file: {gcs_uri}")
            except Exception as e_del:
                print(f"Error deleting GCS file {gcs_uri}: {e_del}\n{traceback.format_exc()}")