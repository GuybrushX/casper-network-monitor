from peer_spider import Spider
from pickle_util import load_pickle

val_perc = load_pickle("data/account_percent.pkl")
s = Spider(['3.14.161.135', '3.12.207.193', '3.142.224.108'], 'casper')
s.get_all_nodes()
perc = s.get_weight_active_percent(val_perc)
print(f"{round(perc, 2)}% weight active.")
