import requests
import asyncio
from collections import defaultdict

STATUS_PORT = '8888'
STATUS_PATH = 'status'


class Spider:
    """
     Uses a seed list of ips to spider the network of peers
    """
    def __init__(self, ip_list: list, network_name):
        self._all_ip = set()
        self._called_ip = set()
        self.network_name = network_name
        self.session = None
        self.nodes = {}
        for ip in ip_list:
            self._all_ip.add(ip)

    @staticmethod
    def _clean_peers(status_peers: list) -> set:
        """
        Translate peers from status response to ip.

        Handles new network style:
        {
            "node_id": "NodeId::P2p(DYf1..p3vF)",
            "address": "/ip4/13.56.210.126/tcp/53686"
        },

        or old network style:
        {
            "node_id": "NodeId::Tls(9fae..c7be)",
            "address": "13.57.200.251:35000"
        }
        """
        peer_ips = []
        for peer in status_peers:
            addr = peer["address"]
            if "/ip4/" in addr and "/tcp/" in addr:
                peer_ips.append(addr.split("/tcp/")[0].split("/ip4/")[1])
            else:
                peer_ips.append(addr.split(":")[0])
        return set(peer_ips)

    def _get_status(self, ip):
        """
        Syncronous status requestor
        :param ip: ip of node
        :return: status result or {"error": error test}
        """
        data = None
        try:
            response = requests.get(f"http://{ip}:{STATUS_PORT}/{STATUS_PATH}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data["chainspec_name"] != self.network_name:
                    raise ValueError("Node in wrong network")
                data["peers"] = Spider._clean_peers(data["peers"])
                data["is_validator"] = False if data["round_length"] is None else True
            else:
                data = {"error": response.text,
                        "code": requests.status_codes}
        except Exception as e:
            data = {"error": e}
        data["ip"] = ip
        return data

    async def _get_status_async(self, ip):
        return await asyncio.get_event_loop().run_in_executor(None, self._get_status, ip)

    async def _get_all_current_status(self):
        """
        async to get status from all peers not queried thus far
        """
        tasks = []
        for ip in self._all_ip - self._called_ip:
            tasks.append(self._get_status_async(ip))
        results = await asyncio.gather(*tasks)
        return results

    def _make_two_way_links(self):
        reverse_link = defaultdict(set)
        for node in self.nodes.values():
            for ip in node["peers"]:
                reverse_link[ip].add(node["ip"])
        for node in self.nodes.values():
            node["peers_of_me"] = reverse_link[node["ip"]]
            node["two_way_peers"] = node["peers"].intersection(node["peers_of_me"])

    def get_all_nodes(self):
        """
        Fires off async requests to get all peers in self._all_ip set not in self._called_ip set.
        This will add ips from peers of each call and loop until all are called.
        """
        self._called_ip = set()
        while len(self._all_ip - self._called_ip) > 0:
            results = asyncio.get_event_loop().run_until_complete(self._get_all_current_status())
            for result in results:
                ip = result["ip"]
                self._called_ip.add(ip)
                if "error" not in result:
                    self.nodes[ip] = result
                    for ip in result["peers"]:
                        self._all_ip.add(ip)
        self._make_two_way_links()

    def active_node_keys(self):
        """
        Returns public keys of active nodes as iterator
        """
        self.get_all_nodes()
        for node in self.nodes.values():
            yield node["our_public_signing_key"]

    def get_weight_active_percent(self, validator_percent):
        """
        Returns active percent weight

        validator_percent is {key: percent_weight} dictionary
        """
        val_keys = set(validator_percent.keys())
        node_keys = set(self.active_node_keys())
        missing_keys = val_keys - node_keys
        for key in missing_keys:
            print(f"{key} - Inactive validator with weight: {round(validator_percent[key], 3)}%")
        active_keys = val_keys.intersection(node_keys)
        return sum([weight for key, weight in validator_percent.items()
                    if key in active_keys])

