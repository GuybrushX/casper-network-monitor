#!/usr/bin/env python3

from peer_spider import Spider, INTERNAL_NODES
from pathlib import Path
from datetime import datetime
import pickle
from network_graph import graph_nodes

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"
IPS_FILE = DATA_FOLDER / "ips.pickle"
NODES_FILE = DATA_FOLDER / f"nodes_{int(datetime.now().timestamp())}.pickle"
LATEST_FILE = DATA_FOLDER / "nodes_latest.pickle"
GRAPH_FILE = DATA_FOLDER / "graph_latest.png"
GRAPH_IPS_LATEST = DATA_FOLDER / "ips_latest.csv"


if not DATA_FOLDER.exists():
    raise Exception(f"{DATA_FOLDER} does not exist.")


def load_ips():
    try:
        if IPS_FILE.exists():
            with open(IPS_FILE, "rb") as f:
                return pickle.load(f)
        return INTERNAL_NODES
    except pickle.UnpicklingError:
        # Should overwrite bad file after generating new ip list
        return INTERNAL_NODES


def save_to_pickle(data, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

ips = load_ips()

spider = Spider(ips)
spider.get_all_nodes()

save_to_pickle(list(spider.nodes.keys()), IPS_FILE)
save_to_pickle(spider.nodes, NODES_FILE)
save_to_pickle(spider.nodes, LATEST_FILE)

ip_list = graph_nodes(spider.nodes, GRAPH_FILE)
GRAPH_IPS_LATEST.write_text('\n'.join([f"{ip},{index}" for index, ip in ip_list]))
