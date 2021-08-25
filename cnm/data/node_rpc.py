import json
import requests
import datetime as dt
import pytz


def rpc_call(url, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    response = requests.request("POST", url, data=payload, headers=headers)
    json_data = json.loads(response.text)
    return json_data["result"]


def time_from_timestamp(timestamp: str):
    time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    era_start_time = dt.datetime.strptime(timestamp, time_format)
    return pytz.utc.localize(era_start_time)


def get_deploy(url: str, deploy_hash: str):
    """
    Get deploy by deploy_hash
    """
    return rpc_call(url, "info_get_deploy", [deploy_hash])


def get_block(url: str, block_hash: str = None, block_height: int = None):
    """
    Get block based on block_hash, block_height, or last block if block_identifier is missing
    """
    params = []
    if block_hash:
        params = [{"Hash": block_hash}]
    elif block_height:
        params = [{"Height": block_height}]
    return rpc_call(url, "chain_get_block", params)

