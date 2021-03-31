#!/usr/bin/env python3

from peer_spider import Spider
from pathlib import Path
from datetime import datetime
from pickle_util import save_bz2_pickle
from network_graph import graph_nodes
from casper_node_util import get_last_auction_era_key_weight, get_current_era_key_weight

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"
NODES_FILE = DATA_FOLDER / "nodes" / f"nodes_{int(datetime.now().timestamp())}.pbz2"
LATEST_FILE = DATA_FOLDER / "nodes_latest.pbz2"
GRAPH_FILE = DATA_FOLDER / "graph_latest.png"
GRAPH_IPS_LATEST = DATA_FOLDER / "ips_latest.csv"


NETWORK_NAME = "casper"
IPS = """3.14.161.135
3.12.207.193
3.142.224.108""".splitlines()

if not DATA_FOLDER.exists():
    raise Exception(f"{DATA_FOLDER} does not exist.")

print("Getting key weight")
cur_key_weight = get_current_era_key_weight(f"http://{IPS[0]}:7777")
cur_total_weight = sum(cur_key_weight.values())
next_key_weight = get_last_auction_era_key_weight(f"http://{IPS[0]}:7777")
next_total_weight = sum(next_key_weight.values())

print("Getting nodes from spider")
spider = Spider(IPS, NETWORK_NAME)
spider.get_all_nodes()
for node in spider.nodes.values():
    key = node["our_public_signing_key"]
    if key in cur_key_weight:
        node["cur_weight"] = next_key_weight.get(key, 0)
        node["cur_weight_percent"] = round(node["cur_weight"] / next_total_weight * 100, 3)
    if key in next_key_weight:
        node["next_weight"] = next_key_weight.get(key, 0)
        node["next_weight_percent"] = round(node["next_weight"] / next_total_weight * 100, 3)

save_bz2_pickle(spider.nodes, NODES_FILE)
save_bz2_pickle(spider.nodes, LATEST_FILE)

print("Graphing nodes")
ip_list = graph_nodes(spider.nodes, GRAPH_FILE)
GRAPH_IPS_LATEST.write_text('\n'.join([f"{ip},{index}" for index, ip in ip_list]))
