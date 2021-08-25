import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
WEB_DATA = Path(os.environ.get("WEB_DATA", SCRIPT_DIR.parent / "data"))
UPLOAD_PATH = Path(os.environ.get("WEB_UPLOAD_DATA", SCRIPT_DIR.parent / "upload_data"))
UPLOAD_ARCHIVE_PATH = Path(os.environ.get("WEB_UPLOAD_DATA", SCRIPT_DIR.parent / "archived"))

WEB_USER = os.environ.get("WEB_USER")
WEB_PASS = os.environ.get("WEB_PASS")

MONGO_USER = "root"
MONGO_PASS = "Secret"
MONGO_SERVER = "localhost"
MONGO_DB = "cnm"
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_SERVER}"
