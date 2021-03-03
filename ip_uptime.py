from pickle_util import load_bz2_pickle
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent.absolute()
NODES_PATH = SCRIPT_DIR / "data_cnm" / "nodes"
IP_UPTIME_PATH = SCRIPT_DIR / "data_cnm" / "ip_uptime.csv"
VALIDATE_IP_PATH = SCRIPT_DIR / "data_cnm" / "validate_ip.pbz2"

vip = load_bz2_pickle(VALIDATE_IP_PATH)
ip_key = {ip: key for key, ip in vip.items()}

ips = defaultdict(int)
check_count = 0

def get_height(status):
    last_added = status.get("last_added_block_info", None)
    if last_added is None:
        return 0
    return last_added.get("height", 0)


files = sorted(list(NODES_PATH.iterdir()))
for file in files:
    print(file)
    height = set()
    check_count += 1
    obj = load_bz2_pickle(file)
    for _, status in obj.items():
        height.add(get_height(status))
    for ip, status in obj.items():
        if abs(get_height(status) - max(height)) <= 2:
            ips[ip] += 1

with open(IP_UPTIME_PATH, 'w') as f:
    for ip, count in sorted(ips.items(), key=lambda d: d[1], reverse=True):
        f.write(f"{ip},{ip_key.get(ip,'???')},{round(count/check_count * 100, 4)}%\n")


