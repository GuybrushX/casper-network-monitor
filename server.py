from flask import Flask, send_file, render_template, abort, request
from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth

from pickle_util import load_bz2_pickle
from pathlib import Path
from collections import defaultdict
from accounts_toml import get_data, GIT_HASH, get_summary
from protocol import get_chainspec_config_readme
from networks import NETWORKS
from config import UPLOAD_PATH, USERNAME, PASSWORD


app = Flask(__name__)
SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"

ALLOWED_EXTENSIONS = {'gz'}
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
# Limit max upload to 100 MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

app.config['BASIC_AUTH_USERNAME'] = USERNAME
app.config['BASIC_AUTH_PASSWORD'] = PASSWORD

basic_auth = BasicAuth(app)


def nodes_latest_path(network_name: str) -> Path:
    return DATA_FOLDER / network_name / "nodes_latest.pbz2"


def image_path(network_name: str) -> Path:
    return DATA_FOLDER / network_name / "graph_latest.png"


def network_info_path(network_name: str) -> Path:
    return DATA_FOLDER / network_name / "network_info.pbz2"


@app.route('/')
def networks():
    return render_template('networks.html', networks=NETWORKS)


@app.route('/debug_upload_script')
def debug_upload_script():
    return send_file(SCRIPT_DIR / "debug_upload_script.sh")


def valid_key(key: str) -> bool:
    if key[:2] == '01':
        return len(key) == 66
    if key[:2] == '02':
        return len(key) == 68
    return False


# Upload with
# curl -F file=@<filename> key=<public_key> ts=<shared timestamp date +%s> http://127.0.0.1:8080/upload_debug_info
@app.route('/upload_debug_info', methods=['POST'])
def upload_debug_info():
    file = request.files['file']
    key = request.form['key']
    ts = request.form['ts']
    if not key:
        return "key not received\n", 400
    else:
        if not valid_key(key):
            return "invalid key\n", 400
    if not file:
        return "file not received\n", 400
    if not ts:
        return "ts not received\n", 400

    save_folder = UPLOAD_PATH / secure_filename(key) / secure_filename(ts)
    save_folder.mkdir(parents=True, exist_ok=True)
    save_path = save_folder / secure_filename(file.filename)
    file.save(save_path)
    return "complete\n", 200


@app.route('/view_debug_info', defaults={'key': None, 'ts': None})
@app.route('/view_debug_info/<key>', defaults={'ts': None})
@app.route('/view_debug_info/<key>/<ts>')
@basic_auth.required
def view_debug_info(key, ts):
    if key is None and ts is None:
        keys = sorted([path.name for path in UPLOAD_PATH.glob('*')])
        return render_template('debug_keys.html', keys=keys)
    if ts is None:
        key_path = UPLOAD_PATH / key
        timestamps = sorted([path.name for path in key_path.glob('*')])
        return render_template('debug_timestamps.html', key=key, timestamps=timestamps)
    full_path = UPLOAD_PATH / key / ts
    logs = sorted([path.name for path in full_path.glob('casper-node.log*gz')])
    err_logs = sorted([path.name for path in full_path.glob('casper-node.stderr.log*gz')])
    configs = sorted([path.name for path in full_path.glob('*_*_*.tar.gz')])
    reports = [path for path in full_path.glob('casper_node_report')]
    if reports:
        report = reports[0].read_text()
    return render_template('debug_full.html',
                           casper_node_report=report,
                           logs=logs,
                           err_logs=err_logs,
                           configs=configs,
                           key=key,
                           ts=ts)


@app.route('/download_debug_info/<key>/<ts>/<file>')
@basic_auth.required
def download_debug_info(key, ts, file):
    return send_file(UPLOAD_PATH / key / ts / file, mimetype="application/gzip")


@app.route('/network/<network_name>/detail')
def nodes(network_name):
    if network_name == 'favicon.ico':
        abort(404)
    nodes = load_bz2_pickle(nodes_latest_path(network_name))
    return render_template('detail.html', nodes=list(nodes.values()), network_name=network_name)


@app.route('/network/<network_name>/img')
def get_image(network_name):
    return send_file(image_path(network_name), mimetype="image/png")


@app.route('/genesis')
def genesis_empty():
    validators, accounts = get_summary()
    total_supply = sum([d[-2] for d in validators])
    total_supply += sum(d[-1] for d in accounts)
    return render_template('genesis_summary.html',
                           validators=validators,
                           accounts=accounts,
                           hash=GIT_HASH,
                           total_supply=total_supply)


@app.route('/genesis/<public_key>')
def genesis(public_key):
    output = get_data(public_key)
    if output["validator"] is None and len(output["delegated_to"]) == 0 and len(output["delegation"]) == 0:
        return "Not Found"
    return render_template('genesis.html', output=output, hash=GIT_HASH)


@app.route('/protocol/<network>/<protocol>')
def protocol(network, protocol):
    chainspec, config, readme = get_chainspec_config_readme(protocol, network)
    return render_template('protocol.html', chainspec=chainspec, config=config, readme=readme)


@app.route('/network/<network_name>/summary')
def network_info(network_name):
    # need to replace with template.
    net_info = load_bz2_pickle(network_info_path(network_name))
    nodes = load_bz2_pickle(nodes_latest_path(network_name))

    valid_ver = defaultdict(int)
    weight_pct = defaultdict(int)
    all_ver = defaultdict(int)
    node_count = 0
    val_count = 0
    for node in nodes.values():
        node_count += 1
        upgrade = "None"
        if node["next_upgrade"]:
            upgrade = node["next_upgrade"]["activation_point"]
        version = f"{node['api_version']} - Upgrade: {upgrade}"
        if node.get("is_validator"):
            weight = node.get("weight_percent", 0)
            weight_pct[version] += weight
            valid_ver[version] += 1
            val_count += 1
        all_ver[version] += 1

    versions = []
    for key, val in all_ver.items():
        versions.append({"version": key,
                         "all_node_pct": round(val / node_count * 100, 2),
                         "val_node_pct": round(valid_ver.get(key, 0) / val_count * 100, 2),
                         "val_wgt_pct": round(weight_pct.get(key, 0), 2)})
    return render_template('summary.html',
                           peer_counts=net_info["peer_count"],
                           path_counts=net_info["path_count"],
                           versions=sorted(versions, key=lambda d: d["version"], reverse=True))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
