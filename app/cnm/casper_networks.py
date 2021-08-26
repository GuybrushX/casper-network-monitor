from dataclasses import dataclass


@dataclass(frozen=True)
class CasperNetwork:
    """
    Holds data for a casper network
    """
    name: str
    ips: list
    protocol_url: str
    rpc_ip: str

    @property
    def rpc_url(self):
        return f"http://{self.rpc_ip}:7777/rpc"


_casper_ips = ["3.14.161.135",
               "3.12.207.193",
               "3.142.224.108"]

_casper_test_ips = ["3.208.91.63", "35.169.197.193"]

_integration_test_ips = ["3.140.179.157", "3.138.177.248", "3.143.158.19", "3.139.47.90", "18.219.25.234"]

NETWORKS = (CasperNetwork(name="casper",
                          ips=_casper_ips,
                          protocol_url="http://genesis.casperlabs.io",
                          rpc_ip="3.14.161.135"),
            CasperNetwork(name="casper-test",
                          ips=_casper_test_ips,
                          protocol_url="https://casper-genesis.make.services",
                          rpc_ip="3.208.91.63"),
            CasperNetwork(name="integration-test",
                          ips=_integration_test_ips,
                          protocol_url="http://genesis.casperlabs.io",
                          rpc_ip="3.140.179.157"))

_NETWORK_MAP = {net.name: net for net in NETWORKS}


def network_by_name(network_name: str):
    """
    Get network config object by network name
    """
    network = _NETWORK_MAP.get(network_name, None)
    if network is None:
        raise ValueError(f"No network_name: '{network_name}' found.")
    return network
