from flask import Flask, send_file, render_template
from pickle_util import load_bz2_pickle
from pathlib import Path
from collections import defaultdict

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


@app.route('/network')
def network_info():
    # need to replace with template.
    net_info = load_bz2_pickle(NETWORK_INFO_PATH)
    nodes = load_bz2_pickle(NODES_LATEST_PATH)
    distinct_upgrades = set()
    valid_upg = defaultdict(int)
    weight_pct = defaultdict(int)
    all_upg = defaultdict(int)
    node_count = 0
    val_count = 0
    for node in nodes.values():
        node_count += 1
        if node["next_upgrade"] is None:
            upgrade = 'None'
        else:
            upgrade = node["next_upgrade"]["activation_point"]
        if node.get("is_validator"):
            weight = node.get("weight_percent", 0)
            weight_pct[upgrade] += weight
            valid_upg[upgrade] += 1
            val_count += 1
        all_upg[upgrade] += 1

    upgrade_states = []
    for key, val in all_upg.items():
        upgrade_states.append({"state": key,
                               "all_node_pct": round(val / node_count * 100, 2),
                               "val_node_pct": round(valid_upg.get(key, 0) / val_count * 100, 2),
                               "val_wgt_pct": round(weight_pct.get(key, 0), 2)})

    return render_template('network.html',
                           peer_counts=net_info["peer_count"],
                           path_counts=net_info["path_count"],
                           upgrade_states=upgrade_states)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
