import os
import subprocess
import json
import time
from collections import defaultdict
from pathlib import Path
from pickle_util import load_bz2_pickle, save_bz2_pickle

NODE_ADDRESS = 'http://3.18.112.103:7777'
CHAIN_NAME = 'delta-10'

GET_GLOBAL_STATE_COMMAND = ["casper-client", "get-global-state-hash", "--node-address", NODE_ADDRESS]

CL_NODE_ADDRESSES = ['http://54.177.84.9:7777', 'http://3.16.135.188:7777', 'http://18.144.69.216:7777',
                     'http://13.57.251.65:7777', 'http://3.14.69.138:7777']
OTHER_NODE_ADDRESSES = ['http://34.220.39.73:7777', ]

SCRIPT_PATH = Path(__file__).parent.absolute()
DATA_PATH = SCRIPT_PATH / "data"


def _subprocess_call(command, expect_text) -> str:
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(timeout=30)
    if expect_text.encode('utf-8') not in stdout:
        raise Exception(f"Command: {command}\n {stderr.decode('utf-8')}")
    return stdout.decode('utf-8')


def _subprocess_call_with_json(command, expect_text) -> dict:
    return json.loads(_subprocess_call(command, expect_text))


def get_auction_info(node_addr):
    command = ["casper-client", "get-auction-info",
               "--node-address", node_addr]
    return _subprocess_call_with_json(command, '"bids":')


def get_last_auction_era(node_addr):
    gai = get_auction_info(node_addr)
    era_validators = gai["result"]["era_validators"]
    return era_validators[-1]


def get_auction_era_key_weight(era):
    return [(v["public_key"], int(v["weight"])) for v in era["validator_weights"]]


def get_global_state_hash():
    response = _subprocess_call_with_json(GET_GLOBAL_STATE_COMMAND, "global_state_hash")
    return response["global_state_hash"]


def get_deploy(deploy_hash: str):
    response = _subprocess_call_with_json(["casper-client", "get-deploy", "--node-address", NODE_ADDRESS, deploy_hash], "result")
    return response


def get_block(block_hash=None):
    command = ["casper-client", "get-block",
               "--node-address", NODE_ADDRESS]
    if block_hash:
        command.append("-b")
        command.append(block_hash)
    return _subprocess_call_with_json(command, "block")


def get_era_info_by_switch_block(block_identifier):
    """ This will return null for 'era_summary' unless given a switch_block hash, which is the last block of an era. """
    command = ["casper-client", "get-era-info-by-switch-block",
               "--node-address", NODE_ADDRESS,
               "--block-identifier", block_identifier]
    return _subprocess_call_with_json(command, "era_summary")


def get_all_blocks():
    """
    retrieves all blocks on chain and caches when possible

    will be REALLY slow with large block downloads as calls are throttled.
    """
    cached_blocks_file = DATA_PATH / "block_cache.pbz2"
    if Path.exists(cached_blocks_file):
        blocks = load_bz2_pickle(cached_blocks_file)
        last_height = blocks[-1]["header"]["height"]
    else:
        blocks = []
        last_height = -1
    block = get_block()["result"]["block"]
    new_blocks = []
    cur_height = block["header"]["height"]
    print(f"Downloading blocks from cur height: {cur_height} down to cached height: {last_height}.")
    for _ in range(cur_height - last_height):
        new_blocks.append(block)
        time.sleep(0.1)
        parent_hash = block["header"]["parent_hash"]
        if parent_hash != '0000000000000000000000000000000000000000000000000000000000000000':
            block = get_block(parent_hash)["result"]["block"]

    new_blocks.reverse()
    blocks.extend(new_blocks)
    save_bz2_pickle(blocks, cached_blocks_file)
    return blocks


def get_proposer_per_block():
    return [(block["header"]["height"], block["header"]["proposer"]) for block in get_all_blocks()]


def get_all_deploys():
    """
    retrieves all deploys on chain and caches

    will be REALLY slow with large downloads as calls are throttled.

    Key "last_height" stores last_height of block deploys have been sync up to.
    """
    cached_deploys_file = DATA_PATH / "deploy_cache.pbz2"
    if Path.exists(cached_deploys_file):
        deploys = load_bz2_pickle(cached_deploys_file)
    else:
        deploys = {}
    cur_height = 0
    cache_height = deploys.get("last_height", 0)
    blocks = get_all_blocks()
    print(f"Downloading deploys from block height {cache_height} to {blocks[-1]['header']['height']}")
    for block in blocks[cache_height - 1:]:
        cur_height = block["header"]["height"]
        if cur_height < cache_height:
            continue
        for deploy_hash in block["header"]["deploy_hashes"]:
            if deploy_hash not in deploys.keys():
                deploys[deploy_hash] = get_deploy(deploy_hash)
    deploys["last_height"] = cur_height
    save_bz2_pickle(deploys, cached_deploys_file)
    return deploys


def get_deploys_by_public_key(public_key):
    for deploy in get_all_deploys().values():
        if isinstance(deploy, int):
            continue
        if deploy["result"]["deploy"]["header"]["account"] == public_key:
            print(deploy)


def get_all_era_info():
    cached_era_info_file = DATA_PATH / "era_info.pbz2"
    if Path.exists(cached_era_info_file):
        era_info = load_bz2_pickle(cached_era_info_file)
        last_era = max(era_info.keys())
    else:
        era_info = {}
        last_era = -1
    blocks = get_all_blocks()
    print(f"Downloading era data from {last_era} to {blocks[-1]['header']['era_id']}")
    last_block_hash = blocks[0]["hash"]
    for block in blocks:
        cur_era = block["header"]["era_id"]
        if last_era < cur_era:
            last_era = cur_era
            era_info_by_switch = get_era_info_by_switch_block(last_block_hash)
            era_info[cur_era] = era_info_by_switch["result"]["era_summary"]
        last_block_hash = block["hash"]
    save_bz2_pickle(era_info, cached_era_info_file)
    return era_info


def unique_state_root_hashes(blocks):
    pre_srh = ''
    for block in blocks:
        header = block["header"]
        srh = header["state_root_hash"]
        if pre_srh != srh:
            pre_srh = srh
            yield header['era_id'], header['height'], srh


def state_root_hash_by_era():
    pre_era = ''
    for block in get_all_blocks():
        era_id = block["header"]["era_id"]
        if era_id != pre_era:
            pre_era = era_id
            yield era_id, block["header"]["state_root_hash"]


def all_validator_keys(era_validators):
    all_keys = set()
    for era in era_validators:
        for key in [validator[0] for validator in era[2]]:
            all_keys.add(key)
    return sorted(list(all_keys))


def save_validator_by_key(era_validators):
    validators = {}
    all_keys = all_validator_keys(era_validators)
    for key in all_keys:
        validators[key] = []
    for era in era_validators:
        cur_vals = era[2]
        keys_in_era = {val[0]: val[1] for val in cur_vals}
        for key in all_keys:
            validators[key] += [keys_in_era.get(key, 0)]
    valid_by_era_path = Path(os.path.realpath(__file__)).parent / "validators_by_era.csv"
    with open(valid_by_era_path, "w+") as f:
        f.write(f"era_id,bonded_validator_count,{','.join(all_keys)}\n")
        for era_id in range(len(era_validators)):
            f.write(f"{era_id}")
            # Get count of non-zero bond validators
            bonds = [1 for key in all_keys if validators[key][era_id] > 0]
            f.write(f",{len(bonds)}")
            # Get count of participants
            # TODO - Can we get bid count in this era?
            for key in all_keys:
                f.write(f",{validators[key][era_id]}")
            f.write("\n")


def save_block_info():
    with open("block_proposer.csv", "w+") as f:
        f.write("era_id,height,hash,proposer\n")
        all_blocks = get_all_blocks()
        for block in all_blocks:
            f.write(
                f'{block["header"]["era_id"]},{block["header"]["height"]},{block["hash"]},{block["header"]["proposer"]}\n')


def get_deploy_hashs_per_block():
    for block in get_all_blocks():
        header = block['header']
        if header['height'] < 999:
            continue
        print(f"{header['era_id']} - {header['height']} - {header['proposer']} - {header['deploy_hashes']}")


def get_proposer_per_era():
    eras = []
    cur_era = -1
    for block in get_all_blocks():
        header = block['header']
        proposer = header['proposer']
        era = header['era_id']
        if cur_era != era:
            cur_era = era
            eras.append(defaultdict(int))
        eras[era][proposer] += 1
    return eras


def cache_all():
    """ This should do what is needed to cache everything """
    # Loads blocks and deploys
    get_all_deploys()
    # Uses blocks to load era_info
    get_all_era_info()

