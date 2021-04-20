from networks import Network
from peer_spider import Spider
from pathlib import Path
from datetime import datetime
from pickle_util import save_bz2_pickle
from network_graph import graph_nodes
from casper_node_util import get_last_auction_era_key_weight


SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"


def save_data(network: Network):
    print(f"Network {network.name}")
    network_folder = DATA_FOLDER / network.name
    nodes_file = network_folder / "nodes" / f"nodes_{int(datetime.now().timestamp())}.pbz2"
    latest_file = network_folder / "nodes_latest.pbz2"
    graph_file = network_folder / "graph_latest.png"
    graph_ips_latest = network_folder / "ips_latest.csv"
    network_info_file_path = network_folder / "network_info.pbz2"
    (network_folder / "nodes").mkdir(parents=True, exist_ok=True)

    print("Getting key weight")
    key_weight = get_last_auction_era_key_weight(f"http://{network.ips[0]}:7777")
    total_weight = sum(key_weight.values())

    print("Getting nodes from spider")
    spider = Spider(network.ips, network.name)
    spider.get_all_nodes()
    for node in spider.nodes.values():
        key = node["our_public_signing_key"]
        if key in key_weight:
            node["weight"] = key_weight.get(key, 0)
            node["weight_percent"] = round(node["weight"] / total_weight * 100, 3)

    save_bz2_pickle(spider.nodes, nodes_file)
    save_bz2_pickle(spider.nodes, latest_file)

    print("Graphing nodes")
    ip_list = graph_nodes(spider.nodes, graph_file, network_info_file_path)
    graph_ips_latest.write_text('\n'.join([f"{ip},{index}" for index, ip in ip_list]))
