"""Tools for the ingestion agent."""
import os
import shutil
import tempfile
import zipfile
from typing import Annotated

from google.cloud import storage

def download_gcs_file() -> Annotated[str, "The local path to the downloaded file."]:
    """Downloads a file from Google Cloud Storage to a local temporary file."""
    client = storage.Client()
    # Use environment variable for bucket and hardcode the object path.
    bucket_name = os.environ.get("GCS_BUCKET_NAME", "datasets-ccibt-hack25ww7-714")
    blob_name = "datasets/uc5-cross-language-code-translation/BankSystem-master.zip"
    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    bucket_name, blob_name = gcs_uri.replace("gs://", "").split("/", 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Create a temporary file and download the blob content into it.
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.basename(blob_name)) as temp_file:
        blob.download_to_file(temp_file)
        return temp_file.name

def unzip_file(
    zip_path: Annotated[str, "The local path to the zip file."],
) -> Annotated[str, "The path to the directory where files were extracted."]:
    """Unzips a file to a new temporary directory."""
    extract_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    os.remove(zip_path)  # Clean up the downloaded zip file
    return extract_dir

def scan_project_structure(
    directory_path: Annotated[str, "The path to the project directory to scan."]
) -> Annotated[
    str, "A JSON string representing the project structure and file contents."
]:
    """Scans a directory to create a JSON representation of its structure."""
    project_structure = {}
    for root, _, files in os.walk(directory_path):
        for name in files:
            file_path = os.path.join(root, name)
            relative_path = os.path.relpath(file_path, directory_path)
            _, extension = os.path.splitext(name)
            project_structure[relative_path] = {"extension": extension}
    return str(project_structure)

def cleanup_directory(
    directory_path: Annotated[str, "The path to the directory to be removed."]
) -> Annotated[str, "A confirmation message."]:
    """Removes a directory and all its contents."""
    shutil.rmtree(directory_path)
    return f"Successfully removed directory: {directory_path}"