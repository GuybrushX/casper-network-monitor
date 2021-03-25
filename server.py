from flask import Flask, send_file, render_template
from pickle_util import load_bz2_pickle
from pathlib import Path
from collections import defaultdict
from accounts_toml import get_data, GIT_HASH

app = Flask(__name__)
SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"
NODES_LATEST_PATH = DATA_FOLDER / "nodes_latest.pbz2"
NETWORK_INFO_PATH = DATA_FOLDER / "network_info.pbz2"
IMAGE_PATH = DATA_FOLDER / "graph_latest.png"


@app.route('/')
def nodes():
    nodes = load_bz2_pickle(NODES_LATEST_PATH)
    return render_template('index.html', nodes=list(nodes.values()), network_name="delta-11")


@app.route('/img')
def get_image():
    return send_file(IMAGE_PATH, mimetype="image/png")


@app.route('/genesis')
def genesis_empty():
    return "Load with public_key_hash as http://cnm.casperlabs.io/genesis/<public_key_hash>"


@app.route('/genesis/<public_key>')
def genesis(public_key):
    output = get_data(public_key)
    if output["validator"] is None and len(output["delegated_to"]) == 0 and len(output["delegation"]) == 0:
        return "Not Found"
    return render_template('genesis.html', output=output, hash=GIT_HASH)


@app.route('/network')
def network_info():
    # need to replace with template.
    net_info = load_bz2_pickle(NETWORK_INFO_PATH)
    nodes = load_bz2_pickle(NODES_LATEST_PATH)

    valid_ver = defaultdict(int)
    weight_pct = defaultdict(int)
    all_ver = defaultdict(int)
    node_count = 0
    val_count = 0
    for node in nodes.values():
        node_count += 1
        version = node["api_version"]
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
    return render_template('network.html',
                           peer_counts=net_info["peer_count"],
                           path_counts=net_info["path_count"],
                           versions=sorted(versions, key=lambda d: d["version"], reverse=True))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
