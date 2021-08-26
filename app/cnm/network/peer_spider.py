import requests
import asyncio

STATUS_PORT = '8888'
STATUS_PATH = 'status'


def get_network_nodes_status(network_name: str, ips: list) -> dict:
    """
    Returns ip key dict of status nodes peers list stripped to ip
    """
    ps = _PeerSpider(network_name, ips)
    ps.query_all_nodes()
    return ps.nodes


class _PeerSpider:
    """
     Uses a seed list of ips to spider the network of peers
    """
    def __init__(self, network_name: str, ips: list):
        if len(ips) < 1:
            raise ValueError("Need minimum of 1 IP in list to spider.")
        self._all_ip = set()
        self._all_ip.update(ips)
        self.network_name = network_name
        self._called_ip = set()
        self._error_ip = set()
        self.nodes = {}

    @staticmethod
    def _clean_peers(status_peers: list) -> list:
        """
        Translate peers from status response to ip.

        {
            "node_id": "NodeId::Tls(9fae..c7be)",
            "address": "13.57.200.251:35000"
        }
        """
        return [peer["address"].split(":")[0] for peer in status_peers]

    def _get_status(self, ip):
        """
        Syncronous status requestor

        :param ip: ip of node
        :return: status result or {"error": error test}
        """
        data = {}
        try:
            response = requests.get(f"http://{ip}:{STATUS_PORT}/{STATUS_PATH}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data["chainspec_name"] != self.network_name:
                    raise ValueError("Node in wrong network")
                data["peers"] = self._clean_peers(data["peers"])
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

    def query_all_nodes(self):
        """
        Fires off async requests to get all peers in self._all_ip set not in self._called_ip set.
        This will add ips from peers of each call and loop until all are called.
        """
        self._called_ip = set()
        self._error_ip = set()
        while len(self._all_ip - self._called_ip) > 0:
            results = asyncio.run(self._get_all_current_status())
            for result in results:
                ip = result["ip"]
                self._called_ip.add(ip)
                if "error" in result:
                    self._error_ip.add(ip)
                self.nodes[ip] = result
                self._all_ip.update(result.get("peers", []))
