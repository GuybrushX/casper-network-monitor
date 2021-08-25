import json
import requests
from datetime import datetime


def rpc_call(url: str, method: str, params: list):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    try:
        response = requests.request("POST", url, data=payload, headers=headers)
        json_data = json.loads(response.text)
        return json_data["result"]
    except requests.exceptions.RequestException as e:
        print(e)
    except Exception as e:
        print(e)


def get_datetime_from_timestamp(timestamp) -> datetime:
    pass


def get_deploy(url: str, deploy_hash: str):
    """
    Get deploy by deploy_hash
    """
    return rpc_call(url, "info_get_deploy", [deploy_hash])


def get_block(url: str, block_hash=None, block_height=None):
    """
    Get block based on block_hash, block_height, or last block if block_identifier is missing
    """
    params = []
    if block_hash:
        params = [{"Hash": block_hash}]
    elif block_height:
        params = [{"Height": block_height}]
    return rpc_call(url, "chain_get_block", params)


def get_auction_info(url: str):
    return rpc_call(url, "state_get_auction_info", [])
