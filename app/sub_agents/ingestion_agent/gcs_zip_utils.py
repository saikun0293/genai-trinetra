"""Utilities for handling GCS zip files and scanning project structure."""

import json
import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Set

from google.cloud import storage

logger = logging.getLogger(__name__)


# File extension to content type mapping for inference
EXTENSION_MAP = {
    # Programming Languages
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "header",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".sh": "shell",
    ".bash": "bash",
    ".zsh": "zsh",
    
    # Markup and Styles
    ".html": "html",
    ".xml": "xml",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "config",
    ".conf": "config",
    
    # Documentation
    ".md": "markdown",
    ".rst": "rst",
    ".txt": "text",
    ".doc": "doc",
    ".docx": "docx",
    ".pdf": "pdf",
    
    # Data
    ".csv": "csv",
    ".tsv": "tsv",
    ".sql": "sql",
    ".db": "database",
    ".sqlite": "sqlite",
    
    # Archives and Compressed
    ".zip": "archive",
    ".tar": "archive",
    ".gz": "archive",
    ".rar": "archive",
    ".7z": "archive",
    
    # Media
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".svg": "image",
    ".mp4": "video",
    ".avi": "video",
    ".mov": "video",
    ".mp3": "audio",
    ".wav": "audio",
    ".flac": "audio",
}

# Extensions to read text content from
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h",
    ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
    ".sh", ".bash", ".zsh", ".html", ".xml", ".css", ".scss", ".sass",
    ".less", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".md", ".rst", ".txt", ".csv", ".tsv", ".sql"
}

# Maximum file size to read (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def download_and_extract_gcs_zip(bucket_name: str, zip_path: str) -> str:
    """
    Download a zip file from GCS and extract it to a temporary folder.
    
    Args:
        bucket_name: The GCS bucket name
        zip_path: The path to the zip file in the bucket
    
    Returns:
        The path to the temporary folder containing extracted files
    
    Raises:
        FileNotFoundError: If the zip file doesn't exist
        ValueError: If the zip file is corrupted
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="gcs_project_")
    logger.info(f"Created temporary directory: {temp_dir}")
    
    try:
        # Initialize GCS client
        logger.info(f"Initializing GCS client for bucket: {bucket_name}")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(zip_path)
        
        # Check if blob exists
        logger.info(f"Checking if zip file exists: gs://{bucket_name}/{zip_path}")
        if not blob.exists():
            logger.error(f"Zip file not found: gs://{bucket_name}/{zip_path}")
            shutil.rmtree(temp_dir)
            raise FileNotFoundError(f"Zip file not found: gs://{bucket_name}/{zip_path}")
        
        logger.info(f"Zip file found. Size: {blob.size} bytes")
        
        # Download zip file to temporary location
        logger.info("Downloading zip file from GCS...")
        zip_temp_path = os.path.join(temp_dir, "download.zip")
        blob.download_to_filename(zip_temp_path)
        logger.info(f"Zip file downloaded successfully to: {zip_temp_path}")
        
        # Create extract directory
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        logger.info(f"Created extraction directory: {extract_dir}")
        
        # Extract zip file
        logger.info("Extracting zip file...")
        with zipfile.ZipFile(zip_temp_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info(f"Zip file extracted successfully to: {extract_dir}")
        
        # Remove the zip file
        os.remove(zip_temp_path)
        logger.info("Temporary zip file cleaned up")
        
        return extract_dir
    
    except Exception as e:
        logger.error(f"Error during download and extraction: {str(e)}", exc_info=True)
        shutil.rmtree(temp_dir)
        raise


def scan_project_structure(root_path: str) -> Dict[str, Any]:
    """
    Scan the project structure and return detailed information.
    
    Args:
        root_path: The root path to scan
    
    Returns:
        A dictionary containing:
            - project_structure: The folder structure as a nested dict
            - file_extensions: List of all extensions found with counts
            - file_types: Inferred file types
            - file_summary: Summary of files by type
            - text_content: Text content from readable files (with size limits)
    """
    logger.info(f"Starting project structure scan of: {root_path}")
    extensions: Dict[str, int] = {}
    file_types: Set[str] = set()
    text_content: Dict[str, str] = {}
    structure: Dict[str, Any] = {}
    
    root = Path(root_path)
    file_count = 0
    
    for file_path in root.rglob("*"):
        if file_path.is_file():
            file_count += 1
            # Get extension
            ext = file_path.suffix.lower()
            extensions[ext if ext else "no_extension"] = extensions.get(ext if ext else "no_extension", 0) + 1
            
            # Infer file type
            if ext in EXTENSION_MAP:
                file_types.add(EXTENSION_MAP[ext])
            
            # Read text content from readable files
            if ext in TEXT_EXTENSIONS and file_path.stat().st_size <= MAX_FILE_SIZE:
                try:
                    relative_path = file_path.relative_to(root)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        text_content[str(relative_path)] = content
                        logger.debug(f"Extracted content from: {relative_path}")
                except Exception as e:
                    logger.debug(f"Could not read file {relative_path}: {str(e)}")
    
    logger.info(f"Scanned {file_count} files")
    logger.info(f"Found {len(extensions)} unique file extensions")
    logger.info(f"Identified {len(file_types)} file types: {sorted(list(file_types))}")
    logger.info(f"Extracted text content from {len(text_content)} files")
    
    # Build folder structure
    logger.info("Building folder structure...")
    structure = _build_folder_structure(root_path)
    logger.info("Folder structure built successfully")
    
    return {
        "project_structure": structure,
        "file_extensions": sorted(
            [{"extension": ext, "count": count} for ext, count in extensions.items()],
            key=lambda x: x["count"],
            reverse=True
        ),
        "file_types": sorted(list(file_types)),
        "file_summary": {
            "total_files": sum(extensions.values()),
            "total_extensions": len(extensions),
            "total_types": len(file_types)
        },
        "text_content": text_content
    }


def _build_folder_structure(path: str, max_depth: int = 10, current_depth: int = 0) -> Dict[str, Any]:
    """
    Recursively build a nested dictionary representing the folder structure.
    
    Args:
        path: The path to scan
        max_depth: Maximum depth to traverse
        current_depth: Current recursion depth
    
    Returns:
        A nested dictionary representing the folder structure
    """
    if current_depth >= max_depth:
        return {}
    
    structure = {
        "type": "folder",
        "name": os.path.basename(path),
        "contents": []
    }
    
    try:
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            
            # Skip common directories to ignore
            if _should_skip_item(item):
                continue
            
            if os.path.isdir(item_path):
                structure["contents"].append(
                    _build_folder_structure(item_path, max_depth, current_depth + 1)
                )
            else:
                file_size = os.path.getsize(item_path)
                ext = os.path.splitext(item)[1].lower()
                structure["contents"].append({
                    "type": "file",
                    "name": item,
                    "extension": ext if ext else "none",
                    "size_bytes": file_size
                })
    except PermissionError:
        pass
    
    return structure


def _should_skip_item(item: str) -> bool:
    """Check if an item should be skipped during scanning."""
    skip_patterns = {
        "__pycache__", ".git", ".gitignore", ".env", "venv", "env",
        "node_modules", ".venv", "dist", "build", ".egg-info",
        ".pytest_cache", ".tox", "htmlcov", ".coverage",
        ".mypy_cache", ".dmypy.json", ".pyre", "__MACOSX"
    }
    return item in skip_patterns or item.startswith(".")


def analyze_project_structure(
    bucket_name: str,
    zip_path: str,
    cleanup: bool = True
) -> Dict[str, Any]:
    """
    Complete pipeline: download GCS zip, extract, and analyze project structure.
    
    Args:
        bucket_name: The GCS bucket name
        zip_path: The path to the zip file in the bucket
        cleanup: Whether to clean up temporary files after analysis
    
    Returns:
        The complete project structure analysis
    """
    logger.info(f"Starting complete project analysis pipeline")
    logger.info(f"Bucket: {bucket_name}, Zip path: {zip_path}, Cleanup: {cleanup}")
    
    temp_dir = download_and_extract_gcs_zip(bucket_name, zip_path)
    logger.info(f"Project extracted to: {temp_dir}")
    
    try:
        logger.info("Beginning project structure analysis...")
        analysis = scan_project_structure(temp_dir)
        analysis["source"] = {
            "bucket": bucket_name,
            "zip_path": zip_path,
            "temp_location": temp_dir
        }
        logger.info("Project structure analysis completed successfully")
        return analysis
    
    finally:
        if cleanup:
            logger.info(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir)
            logger.info("Temporary directory cleaned up successfully")
