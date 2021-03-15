#!/usr/bin/env python3

from peer_spider import Spider
from pathlib import Path
from datetime import datetime
from pickle_util import save_bz2_pickle
from network_graph import graph_nodes

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"
NODES_FILE = DATA_FOLDER / "nodes" / f"nodes_{int(datetime.now().timestamp())}.pbz2"
LATEST_FILE = DATA_FOLDER / "nodes_latest.pbz2"
GRAPH_FILE = DATA_FOLDER / "graph_latest.png"
GRAPH_IPS_LATEST = DATA_FOLDER / "ips_latest.csv"


NETWORK_NAME = "delta-11"
IPS = ['18.144.176.168']

if not DATA_FOLDER.exists():
    raise Exception(f"{DATA_FOLDER} does not exist.")


spider = Spider(IPS, NETWORK_NAME)
spider.get_all_nodes()

save_bz2_pickle(spider.nodes, NODES_FILE)
save_bz2_pickle(spider.nodes, LATEST_FILE)

ip_list = graph_nodes(spider.nodes, GRAPH_FILE)
GRAPH_IPS_LATEST.write_text('\n'.join([f"{ip},{index}" for index, ip in ip_list]))
