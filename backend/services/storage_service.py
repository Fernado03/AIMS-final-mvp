from google.cloud import storage
from backend.config import GCS_BUCKET_NAME

storage_client = storage.Client()

def upload_file(file_stream, blob_name):
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob   = bucket.blob(blob_name)
    file_stream.seek(0)
    blob.upload_from_file(file_stream)
    return f"gs://{GCS_BUCKET_NAME}/{blob_name}"

def delete_blob(blob_name):
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    bucket.blob(blob_name).delete()
