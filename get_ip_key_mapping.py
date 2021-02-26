#!/usr/bin/env python3

from casper_node_util import get_all_transfers
from ipaddress import ip_address
from pickle_util import save_bz2_pickle
from pathlib import Path

VALIDATION_ACCOUNT = '016b74ac7946168a7c206a839a51c7ce03df3501f388b2d286a13bcf99d228dbbb'
VALIDATION_ACCOUNT_PARSED = '7238c7759bf1caaba8f78a80c583013b1dfe673ae7976625d83d8b4a39bc60a3'


def ip_from_dec(number: int) -> str:
    return f"{ip_address(number)}"


def get_transfers_to_validation_account() -> dict:
    account_ip = {}
    for transfer_result in get_all_transfers().values():
        if isinstance(transfer_result, int):
            continue
        result = transfer_result["result"]
        deploy = result["deploy"]
        session = deploy.get("session", None)
        if session is None:
            continue
        transfer = session.get("Transfer", None)
        if transfer is None:
            continue
        target = [arg[1]['bytes'] for arg in transfer['args'] if arg[0] == 'target'][0]
        if target == VALIDATION_ACCOUNT_PARSED:
            source_account = deploy["header"]["account"]
            transfer_id = [arg[1]['parsed'] for arg in transfer['args'] if arg[0] == 'id'][0]
            account_ip[source_account] = ip_from_dec(transfer_id)
    return account_ip


def save_ip_mapping():
    account_ips = get_transfers_to_validation_account()

    SCRIPT_DIR = Path(__file__).parent.absolute()
    DATA_FOLDER = SCRIPT_DIR / "data"
    VALIDATION_FILE = DATA_FOLDER / "validate_ip.pbz2"
    save_bz2_pickle(account_ips, VALIDATION_FILE)
