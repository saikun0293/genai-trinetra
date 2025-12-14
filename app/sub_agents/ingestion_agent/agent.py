import json
import os
import logging
from google.adk.agents.llm_agent import Agent
from .prompt import INGESTION_AGENT_PROMPT
from .gcs_zip_utils import analyze_project_structure

# load env variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


def analyze_gcs_project() -> str:
    """
    Analyze a project from a GCS zip file using environment variables.
    
    Reads the following environment variables:
    - GCS_BUCKET_NAME: The Google Cloud Storage bucket name
    - PROJECT_ZIP_PATH: The path to the zip file within the bucket (e.g., "projects/myproject.zip")
    
    Automatically downloads the zip file from GCS, extracts it to a temporary folder,
    scans the folder structure, identifies file types and extensions, and returns a
    detailed JSON analysis of the project.
    
    Returns:
        A JSON string containing:
        - project_structure: Hierarchical folder and file structure
        - file_extensions: List of all file extensions found with counts
        - file_types: Inferred file types (programming languages, docs, config, etc.)
        - file_summary: Summary statistics
        - text_content: Readable text/code files from the project
    
    Raises:
        ValueError: If required environment variables are not set
    """
    logger.info("Starting GCS project analysis...")
    
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    zip_path = os.environ.get("PROJECT_ZIP_PATH")
    
    logger.debug(f"GCS_BUCKET_NAME: {bucket_name}")
    logger.debug(f"PROJECT_ZIP_PATH: {zip_path}")
    
    if not bucket_name:
        logger.error("Missing environment variable: GCS_BUCKET_NAME")
        return json.dumps({
            "error": "Missing environment variable",
            "message": "GCS_BUCKET_NAME environment variable is not set"
        })
    
    if not zip_path:
        logger.error("Missing environment variable: PROJECT_ZIP_PATH")
        return json.dumps({
            "error": "Missing environment variable",
            "message": "PROJECT_ZIP_PATH environment variable is not set"
        })
    
    logger.info(f"Environment variables validated. Bucket: {bucket_name}, Zip path: {zip_path}")
    
    try:
        logger.info("Calling analyze_project_structure...")
        analysis = analyze_project_structure(bucket_name, zip_path, cleanup=True)
        logger.info("Project analysis completed successfully")
        logger.debug(f"Analysis keys: {list(analysis.keys())}")
        return json.dumps(analysis, indent=2, default=str)
    except FileNotFoundError as e:
        logger.error(f"Zip file not found: {str(e)}")
        return json.dumps({
            "error": str(e),
            "message": f"Could not find zip file: {zip_path} in bucket: {bucket_name}"
        })
    except Exception as e:
        logger.error(f"Failed to analyze project structure: {str(e)}", exc_info=True)
        return json.dumps({
            "error": str(e),
            "message": f"Failed to analyze project structure: {str(e)}"
        })


root_agent = Agent(
    model='gemini-2.5-flash',
    name='ingestion_agent',
    description='A helpful assistant for analyzing project structures from GCS zip files.',
    instruction=INGESTION_AGENT_PROMPT,
    tools=[analyze_gcs_project],
)
