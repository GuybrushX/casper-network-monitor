from pathlib import Path
from app.cnm.main import app

# This script is to run locally when developing.  Expected run is with docker-compose to have nginx serving.

SCRIPT_DIR = Path(__file__).parent.absolute()
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.static_folder = SCRIPT_DIR / "static"
app.run(host="0.0.0.0", port="8080")
