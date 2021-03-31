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
IPS = '''    "address": "178.238.235.196:35000"
    "address": "47.242.53.164:35000"
    "address": "135.181.216.81:35000"
    "address": "168.119.137.143:35000"
    "address": "54.39.129.78:35000"
    "address": "135.181.165.110:35000"
    "address": "134.209.16.172:35000"
    "address": "46.4.91.24:35000"
    "address": "134.122.45.61:35000"
    "address": "99.81.225.72:35000"
    "address": "47.251.14.254:35000"
    "address": "207.246.114.236:35000"
    "address": "101.36.120.117:35000"
    "address": "3.17.72.47:35000"
    "address": "63.33.251.206:35000"
    "address": "3.14.161.135:35000"
    "address": "18.188.152.102:35000"
    "address": "34.122.31.70:35000"
    "address": "54.215.53.35:35000"
    "address": "54.39.133.124:35000"
    "address": "51.89.232.234:35000"
    "address": "135.181.116.109:35000"
    "address": "157.90.131.121:35000"
    "address": "157.90.131.49:35000"
    "address": "178.33.239.236:35000"
    "address": "46.101.61.107:35000"
    "address": "31.7.207.16:35000"
    "address": "35.169.205.205:35000"
    "address": "82.95.0.200:35000"
    "address": "139.162.132.144:35000"
    "address": "148.251.190.103:35000"
    "address": "148.251.135.60:35000"
    "address": "134.209.110.11:35000"
    "address": "98.149.220.243:35000"
    "address": "1.15.171.36:35000"
    "address": "62.171.135.101:35000"
    "address": "168.119.209.31:35000"
    "address": "18.219.70.138:35000"
    "address": "157.90.106.242:35000"
    "address": "45.76.251.225:35000"
    "address": "209.145.60.74:35000"
    "address": "47.88.87.63:35000"
    "address": "135.181.134.57:35000"
    "address": "88.99.95.7:35000"
    "address": "188.40.83.254:35000"
    "address": "54.151.24.120:35000"
    "address": "165.22.252.48:35000"
    "address": "168.119.69.6:35000"
    "address": "3.12.207.193:35000"
    "address": "167.172.32.44:35000"
    "address": "54.39.129.79:35000"
    "address": "134.209.243.124:35000"
    "address": "18.191.239.36:35000"
    "address": "3.225.191.9:35000"
    "address": "13.58.71.180:35000"
    "address": "94.130.107.198:35000"
    "address": "18.188.103.230:35000"
    "address": "3.142.224.108:35000"
    "address": "35.152.42.229:35000"
    "address": "62.171.177.179:35000"
    "address": "52.207.122.179:35000"
    "address": "54.180.220.20:35000"
    "address": "62.171.172.72:35000"
    "address": "54.252.66.23:35000"
    "address": "206.189.47.102:35000"
    "address": "3.221.194.62:35000"
'''.splitlines()

IPS = [ip.strip().split(': "')[1].split(':35000"')[0] for ip in IPS]
# IPS = ['18.220.220.20']

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
