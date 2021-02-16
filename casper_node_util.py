import os
import subprocess
import json
import pathlib
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


def get_all_blocks():
    """
    retrieves all blocks on chain and caches when possible

    will be REALLY slow with large block downloads as calls are throttled.
    """
    cached_blocks_file = DATA_PATH / "block_cache.pbz2"
    if pathlib.Path.exists(cached_blocks_file):
        blocks = load_bz2_pickle(cached_blocks_file)
        last_height = blocks[-1]["header"]["height"]
    else:
        blocks = []
        last_height = -1
    block = get_block()["result"]["block"]
    new_blocks = []
    cur_height = block["header"]["height"]
    print(f"Downloading from cur height: {cur_height} down to cached height: {last_height}.")
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
    """
    cached_deploys_file = DATA_PATH / "deploy_cache.pbz2"
    if pathlib.Path.exists(cached_deploys_file):
        deploys = load_bz2_pickle(cached_deploys_file)
    else:
        deploys = {}
    for block in get_all_blocks():
        for deploy_hash in block["header"]["deploy_hashes"]:
            if deploy_hash not in deploys.keys():
                deploys[deploy_hash] = get_deploy(deploy_hash)
    save_bz2_pickle(deploys, cached_deploys_file)
    return deploys

# current_global_state_hash = get_global_state_hash()
# print(get_era_validators(current_global_state_hash))
# all_blocks = get_all_blocks()


#


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


# def filtered_era_validators():
#     cached_eras_file = pathlib.Path(os.path.realpath(__file__)).parent / "era_validator_cache"
#     if pathlib.Path.exists(cached_eras_file):
#         eras = pickle.load(open(cached_eras_file, "rb"))
#     else:
#         eras = []
#     pre_eras = [era[0] for era in eras]
#     for era_id, srh in state_root_hash_by_era(get_all_blocks()):
#         if era_id in pre_eras:
#             continue
#         era_val = get_era_validators(srh)
#         for era in era_val:
#             if era not in eras:
#                 eras.append(era)
#     pickle.dump(eras, open(cached_eras_file, "wb"))
#     return eras


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
    valid_by_era_path = pathlib.Path(os.path.realpath(__file__)).parent / "validators_by_era.csv"
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


# save_block_info()
#get_deploy_hashs_per_block()
# for block in get_all_blocks():
#     # print(block)
#     header = block["header"]
#     deploy_count = len(header['deploy_hashes'])
#     for deploy in header['deploy_hashes']:
#         deploy_obj = get_deploy(deploy)
#         print(deploy_obj)
#     transfer_count = len(header['transfer_hashes'])
#     if deploy_count > 2 or transfer_count > 2:
#         print(f"{header['era_id']}-{header['height']} {deploy_count} {transfer_count}")


# for deploy in get_all_deploys():
#     print(deploy)
#
# era_proposers = get_proposer_per_era()
# print(era_proposers)
# for era_id, era in enumerate(era_proposers):
#     print(era_id, list(era.values()))
# for deploy_hash, deploy in get_all_deploys().items():
#     execution_results = deploy["result"]["execution_results"]
#     if not execution_results:
#         print(f"{deploy_hash} - No execution results.")
#         continue
#     for results in execution_results:
#         if 'Failure' in results["result"].keys():
#             print(results)


# era_validators = filtered_era_validators(all_blocks)
# save_validator_by_key(era_validators)

# state_root_hash_by_era(all_blocks)

# print(get_era_validators(all_blocks[-1]["header"]["state_root_hash"]))

#
# for i in range(10):
#     for node in CL_NODE_ADDRESSES:
#          deploy_do_nothing_to_node(node)
#     time.sleep(65.5)

# for node in CL_NODE_ADDRESSES:
#     deploy_saved_deploy_to_node(node, '~/repos/casper-node/do_nothing_deploy')

def get_weight_differences():
    key_weight = get_auction_era_key_weight(get_last_auction_era(NODE_ADDRESS))
    max_weight = max([v[1] for v in key_weight])
    return [(v[0], max_weight - v[1]) for v in key_weight]


def balance_by_delegation():
    for pub_key, to_delegate in get_weight_differences():
        if to_delegate == 0:
            continue
        command = ["casper-client", "put-deploy",
                   "--chain-name", "delta-10",
                   "--node-address", NODE_ADDRESS,
                   "--secret-key", "/home/sacherjj/aws/keys/joe/secret_key.pem",
                   "--session-path", "/home/sacherjj/repos/casper-node/target/wasm32-unknown-unknown/release/delegate.wasm",
                   "--payment-amount", "1000000000",
                   "--session-arg", f"\"validator:public_key='{pub_key}'\"",
                   "--session-arg", f"\"amount:u512='{to_delegate}'\"",
                   "--session-arg", "\"delegator:public_key='0186d42bacf67a4b6c5042edba6bc736769171ca3320f7b0040ab9265aca13bbee'\""]
        print(' '.join(command))
#
# balance_by_delegation()
