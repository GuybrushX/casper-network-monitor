from flask import Flask, send_file, render_template
from pickle_util import load_bz2_pickle
from pathlib import Path
from collections import defaultdict
from accounts_toml import get_data, GIT_HASH, get_summary
from protocol import get_chainspec_config_readme
from networks import NETWORKS


app = Flask(__name__)
SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"


def nodes_latest_path(network_name: str) -> Path:
    return DATA_FOLDER / network_name / "nodes_latest.pbz2"


def image_path(network_name: str) -> Path:
    return DATA_FOLDER / network_name / "graph_latest.png"


def network_info_path(network_name: str) -> Path:
    return DATA_FOLDER / network_name/ "network_info.pbz2"


@app.route('/')
def networks():
    return "/n".join([net.name for net in NETWORKS])


@app.route('/<network_name>')
def nodes(network_name):
    nodes = load_bz2_pickle(nodes_latest_path(network_name))
    return render_template('index.html', nodes=list(nodes.values()), network_name=network_name)


@app.route('/<network_name>/img')
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


@app.route('/<network>/<protocol>')
def protocol(network, protocol):
    chainspec, config, readme = get_chainspec_config_readme(protocol, network)
    return render_template('protocol.html', chainspec=chainspec, config=config, readme=readme)


@app.route('/<network_name>/network')
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
