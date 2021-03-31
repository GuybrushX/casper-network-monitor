from peer_spider import Spider
from pickle_util import load_pickle

s = Spider(['3.14.161.135'], "casper-dryrun")
val_perc = load_pickle("data/account_percent.pkl")
perc = s.get_weight_active_percent(val_perc)
print(f"{round(perc, 2)}% weight active.")
