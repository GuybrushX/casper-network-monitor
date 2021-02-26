#!/usr/bin/env python3

from peer_spider import Spider, INTERNAL_NODES
from pathlib import Path
from datetime import datetime
from pickle_util import load_bz2_pickle, save_bz2_pickle
from network_graph import graph_nodes
from casper_node_util import cache_all
from get_ip_key_mapping import save_ip_mapping

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"
IPS_FILE = DATA_FOLDER / "ips.bpz2"
NODES_FILE = DATA_FOLDER / f"nodes_{int(datetime.now().timestamp())}.pbz2"
LATEST_FILE = DATA_FOLDER / "nodes_latest.pbz2"
GRAPH_FILE = DATA_FOLDER / "graph_latest.png"
GRAPH_IPS_LATEST = DATA_FOLDER / "ips_latest.csv"


if not DATA_FOLDER.exists():
    raise Exception(f"{DATA_FOLDER} does not exist.")


def load_ips():
    try:
        if IPS_FILE.exists():
            return load_bz2_pickle(IPS_FILE)
        return INTERNAL_NODES
    except Exception:
        # Should overwrite bad file after generating new ip list
        return INTERNAL_NODES


ips = load_ips()

spider = Spider(ips)
spider.get_all_nodes()

save_bz2_pickle(list(spider.nodes.keys()), IPS_FILE)
save_bz2_pickle(spider.nodes, NODES_FILE)
save_bz2_pickle(spider.nodes, LATEST_FILE)

ip_list = graph_nodes(spider.nodes, GRAPH_FILE)
GRAPH_IPS_LATEST.write_text('\n'.join([f"{ip},{index}" for index, ip in ip_list]))

# Cache blocks and deploys
# These are run here currently to eliminate contention with single file data stores.  Needs improvement.
cache_all()
save_ip_mapping()

