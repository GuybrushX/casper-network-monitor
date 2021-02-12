from peer_spider import Spider, INTERNAL_NODES
from pathlib import Path
from datetime import datetime
import pickle

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_FOLDER = SCRIPT_DIR / "data"
IPS_FILE = DATA_FOLDER / "ips.pickle"
NODES_FILE = DATA_FOLDER / f"nodes_{int(datetime.now().timestamp())}.pickle"


def load_ips():
    if IPS_FILE.exists():
        with open(IPS_FILE, "rb") as f:
            return pickle.load(f)
    return INTERNAL_NODES


def save_to_pickle(data, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

ips = load_ips()

spider = Spider(ips)
spider.get_all_nodes()

save_to_pickle(list(spider.nodes.keys()), IPS_FILE)
save_to_pickle(spider.nodes, NODES_FILE)
