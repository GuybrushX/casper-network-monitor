from flask import Flask, send_file
from pickle_util import load_bz2_pickle
from pathlib import Path

app = Flask(__name__)
SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"


@app.route('/')
def get_image():
    return send_file("data/graph_latest.png", mimetype='image/png')


@app.route('/ips')
def ips():
    return send_file("data/ips_latest.csv", mimetype='text/text')


@app.route('/verify/<key>')
def verify_key(key):
    VALIDATION_FILE = DATA_FOLDER / "validate_ip.pbz2"
    ip_dict = load_bz2_pickle(VALIDATION_FILE)
    if key in ip_dict:
        return "IP registered."
    return "IP not registered."


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
