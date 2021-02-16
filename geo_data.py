from pathlib import Path
from pickle_util import load_bz2_pickle, save_bz2_pickle
import requests

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR / "data"
GEO_DATA = DATA_DIR / "geo_data.pbz2"
ACCESS_KEY_FILE = SCRIPT_DIR / "ipstack_access_key"

ACCESS_KEY = ACCESS_KEY_FILE.read_text()


def geo_data_for_ip(ip) -> dict:
    geo_data = load_bz2_pickle(GEO_DATA) if GEO_DATA.exists() else {}
    if ip not in geo_data:
        geo_response = requests.get(f"http://api.ipstack.com/{ip}?access_key={ACCESS_KEY}")
        if geo_response.status_code == 200:
            geo_data[ip] = geo_response.json()
        save_bz2_pickle(geo_data, GEO_DATA)
    return geo_data[ip]
