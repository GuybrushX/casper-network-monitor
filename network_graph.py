import networkx as nx
import matplotlib.pyplot as plt
from peer_spider import Spider, INTERNAL_NODES
import pickle
from pathlib import Path

NODE_FILE = Path("node_status.dat")
CACHED_MODE = False

def load_nodes():
    if NODE_FILE.exists():
        with open(NODE_FILE, "rb") as f:
            return pickle.load(f)
    return None


def save_nodes(nodes):
    with open(NODE_FILE, "wb") as f:
        pickle.dump(nodes, f)

g = nx.Graph()
nodes = load_nodes()
if nodes is None and not CACHED_MODE:
    spider = Spider(INTERNAL_NODES)
    spider.get_all_nodes()
    nodes = spider.nodes
    save_nodes(nodes)

ips = []


def get_ip_index(ip):
    global ips
    try:
        index = ips.index(ip)
    except ValueError:
        index = len(ips)
        ips.append(ip)
    return index


for node in nodes.values():
    ip = node["ip"]
    for peer_ip in node["peers"]:
        g.add_edge(get_ip_index(ip), get_ip_index(peer_ip))
plt.figure(1, figsize=(20, 20))
nx.draw(g, with_labels=True)
plt.show()

for index, value in enumerate(ips):
    print(f"{index} - {value}")
