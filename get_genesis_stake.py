import requests
from tempfile import TemporaryDirectory
import tarfile
import toml
from pickle_util import save_pickle

# Generates a key to weight percent dictionary from config.tar.gz at
# a certain path, but downloading and parsing.


PULL_URL = "http://genesis.casperlabs.io"
NETWORK_NAME = "casper"
PROTOCOL = "1_0_0"
CONFIG_ARCHIVE = "config.tar.gz"
SAVE_FILE_NAME = "account_percent.pkl"

accounts_toml = None
with TemporaryDirectory() as temp_dir:
    r = requests.get(f"{PULL_URL}/{NETWORK_NAME}/{PROTOCOL}/{CONFIG_ARCHIVE}")
    archive_path = f"{temp_dir}/{CONFIG_ARCHIVE}"
    with open(archive_path, "wb") as f:
        f.write(r.content)
    with tarfile.TarFile.open(archive_path) as tf:
        for member in tf.getmembers():
            f = tf.extractfile(member)
            if member.name.endswith("accounts.toml"):
                accounts_toml = toml.loads(f.read().decode("UTF-8"))

account_weight = {}
for account in accounts_toml["accounts"]:
    validator = account.get("validator", None)
    if validator is not None:
        key = account["public_key"]
        weight = int(validator["bonded_amount"])
        account_weight[key] = weight

for delegator in accounts_toml["delegators"]:
    try:
        val_key = delegator["validator_public_key"]
        weight = int(delegator["delegated_amount"])
        account_weight[val_key] += weight
    except KeyError:
        print(f"{delegator['validator_public_key']} not in validators")

total_weight = sum(weight for weight in account_weight.values())

account_percent = {}
for key, weight in account_weight.items():
    account_percent[key] = weight/total_weight * 100

save_pickle(account_percent, f"data/{SAVE_FILE_NAME}")
