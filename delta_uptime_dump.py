# from amazon_redshift_config import ODBC_DRIVER
#
#
# import pyodbc
# cnxn = pyodbc.connect(ODBC_DRIVER)
# cur = cnxn.cursor()
# cur.execute("SELECT now();")
#
# row = cur.fetchone()
#
# print(row)

from pathlib import Path
from pickle_util import load_bz2_pickle

data_path = Path("/home/sacherjj/delta_data")


def dump_d11():
    delta_11_nodes = data_path / "nodes"

    with open(data_path / "delta_11_participation.dat", "w+") as f:
        for filename in delta_11_nodes.glob("*.pbz2"):
            timestamp = int(filename.name.split(".pbz2")[0].split("nodes_")[-1])
            print(timestamp)
            data = load_bz2_pickle(filename)
            for ip, status in data.items():
                key = status["our_public_signing_key"]
                chainspec = status["chainspec_name"]
                build_version = status["build_version"]
                next_upgrade = status["next_upgrade"]
                if next_upgrade:
                    activation_point = int(next_upgrade["activation_point"])
                    protocol_version = next_upgrade["protocol_version"] = "1.0.3"
                else:
                    activation_point = ""
                    protocol_version = ""
                api_version = status["api_version"]
                peer_count = len(status["peers"])
                labi = status["last_added_block_info"]
                if labi:
                    era_id = int(labi["era_id"])
                    height = int(labi["height"])
                else:
                    era_id = ""
                    height = ""
                wdata = [timestamp, ip, key, chainspec, build_version, api_version, peer_count, era_id, height, activation_point, protocol_version]
                f.write("|".join([str(d) for d in wdata]) + "\n")

def dump_d10():
    delta_10_nodes = data_path / "nodes-delta-10"
    d10_validate_ip = data_path / "validate_ip.pbz2"

    vip = load_bz2_pickle(d10_validate_ip)
    rvip = {ip: key for key, ip in vip.items()}

    with open(data_path / "delta_10_participation.dat", "w+") as f:
        for filename in delta_10_nodes.glob("*.pbz2"):
            timestamp = int(filename.name.split(".pbz2")[0].split("nodes_")[-1])
            print(timestamp)
            data = load_bz2_pickle(filename)
            for ip, status in data.items():
                key = rvip.get(ip, "")
                chainspec = status["chainspec_name"]
                build_version = status["build_version"]
                next_upgrade = status["next_upgrade"]
                if next_upgrade:
                    activation_point = int(next_upgrade["activation_point"])
                    protocol_version = next_upgrade["protocol_version"] = "1.0.3"
                else:
                    activation_point = ""
                    protocol_version = ""
                api_version = status["api_version"]
                peer_count = len(status["peers"])
                labi = status["last_added_block_info"]
                if labi:
                    era_id = int(labi["era_id"])
                    height = int(labi["height"])
                else:
                    era_id = ""
                    height = ""
                wdata = [timestamp, ip, key, chainspec, build_version, api_version, peer_count, era_id, height, activation_point, protocol_version]
                f.write("|".join([str(d) for d in wdata]) + "\n")


dump_d11()
