from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", "")

# Directory for uploaded images
UPLOAD_DIR = Path("uploaded_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)