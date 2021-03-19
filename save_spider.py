#!/usr/bin/env python3

from peer_spider import Spider
from pathlib import Path
from datetime import datetime
from pickle_util import save_bz2_pickle
from network_graph import graph_nodes
from casper_node_util import get_last_auction_era_key_weight

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"
NODES_FILE = DATA_FOLDER / "nodes" / f"nodes_{int(datetime.now().timestamp())}.pbz2"
LATEST_FILE = DATA_FOLDER / "nodes_latest.pbz2"
GRAPH_FILE = DATA_FOLDER / "graph_latest.png"
GRAPH_IPS_LATEST = DATA_FOLDER / "ips_latest.csv"


NETWORK_NAME = "delta-11"
IPS = """18.144.176.168
103.149.26.208
104.236.5.144
104.248.195.218
104.248.195.42
107.22.247.79
108.61.211.90
116.202.106.191
116.202.11.79
116.202.17.49
116.202.24.91
116.203.133.78
116.203.150.238
116.203.157.37
116.203.182.37
116.203.19.95
116.203.190.238
116.203.206.169
116.203.214.160
116.203.38.208
116.203.69.88
116.203.95.147
118.189.191.191
13.57.200.251
13.58.71.180
13.69.81.191
134.122.14.111
134.209.16.172
135.181.103.121
135.181.116.109
135.181.129.210
135.181.134.142
135.181.134.57
135.181.147.7
135.181.158.180
135.181.158.217
135.181.158.218
135.181.162.15
135.181.165.110
135.181.177.40
135.181.179.150
135.181.182.96
135.181.192.149
135.181.193.147
135.181.194.188
135.181.195.45
135.181.199.216
135.181.201.14
135.181.24.235
135.181.25.231
135.181.25.45
135.181.250.253
135.181.30.191
135.181.36.98
135.181.40.95
135.181.42.149
135.181.5.16""".splitlines()

if not DATA_FOLDER.exists():
    raise Exception(f"{DATA_FOLDER} does not exist.")

print("Getting key weight")
key_weight = get_last_auction_era_key_weight(f"http://{IPS[0]}:7777")
total_weight = sum(key_weight.values())

print("Getting nodes from spider")
spider = Spider(IPS, NETWORK_NAME)
spider.get_all_nodes()
for node in spider.nodes.values():
    key = node["our_public_signing_key"]
    if key in key_weight:
        node["weight"] = key_weight.get(key, 0)
        node["weight_percent"] = round(node["weight"] / total_weight * 100, 3)

save_bz2_pickle(spider.nodes, NODES_FILE)
save_bz2_pickle(spider.nodes, LATEST_FILE)

print("Graphing nodes")
ip_list = graph_nodes(spider.nodes, GRAPH_FILE)
GRAPH_IPS_LATEST.write_text('\n'.join([f"{ip},{index}" for index, ip in ip_list]))
