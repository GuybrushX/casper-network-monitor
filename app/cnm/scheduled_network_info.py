from time import time
from collections import defaultdict

from .network.node_rpc import get_auction_info
from .network.peer_spider import get_network_nodes_status
from .casper_networks import CasperNetwork, network_by_name
from .data.file_spider import FileSpider
from .data.file_network_detail import FileNetworkDetail
from .data.file_network_summary import FileNetworkSummary

from .config import WEB_DATA


class NetworkInfo:

    def __init__(self, network_config: CasperNetwork):
        self.config: CasperNetwork = network_config
        self.statuses = None
        self.errored = []
        self.auction_info = None
        self.era_key_weights = []
        self.total_weights = []

    def _process_auction_info(self):
        self.key_bids = {bid["public_key"]: bid["bid"] for bid in self.auction_info["auction_state"]["bids"]}
        era_vals = self.auction_info["auction_state"]["era_validators"]
        for bid in era_vals:
            total_weight = 0
            key_weights_map = {}
            for kw in bid["validator_weights"]:
                key_weights_map[kw["public_key"]] = int(kw["weight"])
                total_weight += int(kw["weight"])
            self.era_key_weights.append(key_weights_map)
            self.total_weights.append(total_weight)

    def _add_status_data(self):
        for ip, node in self.statuses.items():
            if node.get("error", False):
                self.errored.append(ip)
                continue
            key = node.get("our_public_signing_key", None)
            for ind, name in zip(range(0, 2), ('cur', 'next')):
                weight = self.era_key_weights[ind].get(key, None)
                if weight is not None:
                    node[f"{name}_weight"] = weight
                    if self.total_weights[ind] > 0:
                        node[f"{name}_percent"] = round(weight * 100 / self.total_weights[ind], 2)
            bid = self.key_bids.get(key)
            if bid is None:
                continue
            node["staked_amount"] = bid.get("staked_amount")
            node["delegation_rate"] = bid.get("delegation_rate")
            node["inactive"] = bid.get("inactive")

    def _remove_bad_ips(self):
        for ip in self.errored:
            del self.statuses[ip]

    def _make_detail(self):
        details = {"fields": ["IP",
                              "Public Key",
                              "Peers Len",
                              "API Version",
                              "Network",
                              "Starting State Root Hash",
                              "Round Length",
                              "Build Version",
                              "Cur Weight",
                              "Cur Era %",
                              "Next Weight",
                              "Next Era %",
                              "Staked Amount",
                              "Delegation Rate",
                              "Inactive",
                              "Block Hash",
                              "Timestamp",
                              "Era Id",
                              "Height",
                              "State Root Hash",
                              "Proposer",
                              "Activation Point",
                              "Protocol Version"],
                   "data": []}
        for status in self.statuses.values():
            cur_detail = [status.get("ip"),
                          status.get("our_public_signing_key"),
                          len(status.get("peers", [])),
                          status.get("api_version"),
                          status.get("chainspec_name"),
                          status.get("starting_state_root_hash"),
                          status.get("round_length"),
                          status.get("build_version"),
                          status.get("cur_weight"),
                          status.get("cur_percent"),
                          status.get("next_weight"),
                          status.get("next_percent"),
                          status.get("staked_amount"),
                          status.get("delegation_rate"),
                          status.get("inactive")]
            labi = status.get("last_added_block_info")
            if labi is None:
                labi = {}
            cur_detail.extend([labi.get("hash"),
                               labi.get("timestamp"),
                               labi.get("era_id"),
                               labi.get("height"),
                               labi.get("state_root_hash"),
                               labi.get("creator")])
            upgrade = status.get("next_upgrade")
            if upgrade is None:
                upgrade = {}
            cur_detail.extend([upgrade.get("activation_point"),
                               upgrade.get("protocol_version")])
            details["data"].append(cur_detail)
        return details

    def _make_summary(self, nodes):
        valid_ver = defaultdict(int)
        weight_pct = defaultdict(int)
        all_ver = defaultdict(int)
        node_count = 0
        val_count = 0
        for node in nodes:
            node_count += 1
            upgrade = None
            if node["next_upgrade"]:
                upgrade = node["next_upgrade"]["activation_point"]
            version = node['api_version'], upgrade
            if node.get("cur_weight", 0) > 0:
                val_count += 1
                valid_ver[version] += 1
            weight_pct[version] += node.get("cur_percent", 0)
            all_ver[version] += 1

        versions = []
        for key, val in all_ver.items():
            versions.append({"version": key,
                             "all_pct": round(val / node_count * 100, 2),
                             "all_cnt": val,
                             "val_pct": round(valid_ver.get(key, 0) / val_count * 100, 2),
                             "val_cnt": val_count,
                             "val_wgt_pct": round(weight_pct.get(key, 0), 2)})
        return versions

    @property
    def last_block_time(self):
        max_height = 0
        max_timestamp = None
        for status in self.statuses.values:
            labi = status.get("last_added_block_info")
            if labi is None:
                continue
            height = labi.get("height")
            if max_height < height:
                max_height = height
                max_timestamp = labi.get("timestamp")

        return

    def _make_links(self, statuses):
        pass

    def _near_tip_status(self, blocks_off_max: int):
        max_height = 0
        for status in self.statuses.values():
            labi = status.get("last_added_block_info")
            if labi is None:
                continue
            max_height = max(max_height, labi.get("height", 0))
        must_be_height = max_height - blocks_off_max
        for status in self.statuses.values():
            labi = status.get("last_added_block_info")
            if labi is None:
                continue
            if labi.get("height", 0) >= must_be_height:
                yield status

    def generate(self):
        """
        Slow method that spiders network and saves data for network detail, summary and other pages.
        """
        self.statuses = get_network_nodes_status(self.config.name, self.config.ips)
        self.auction_info = get_auction_info(self.config.rpc_url)
        self._process_auction_info()
        self._add_status_data()
        # If you don't strip errors out, getting TypeError: cannot pickle 'module' object
        # Even converting to string this is happening.  Odd.  Was trying to save errors and strip before detail.
        self._remove_bad_ips()
        FileSpider(self.config.name, WEB_DATA, self.statuses).save()
        FileNetworkDetail(self.config.name, WEB_DATA, self._make_detail()).save()
        tip_status = list(self._near_tip_status(3))
        summary = {"full": self._make_summary(self.statuses.values()),
                   "top": self._make_summary(tip_status),
                   "full_links": self._make_links(self.statuses.values()),
                   "top_links": self._make_links(tip_status)}


    # @staticmethod
    # def generate_network_info(network_name: str):
    #     """
    #     Slow method that spiders network and saves data for network detail, summary and other pages.
    #     """
    #     net_config: CasperNetwork = network_by_name(network_name)
    #     nodes_status = get_network_nodes_status(network_name, net_config.ips)
    #     auction_info = get_auction_info(net_config.rpc_url)
    #
    #     key_bids = {bid["public_key"]: bid["bid"] for bid in auction_info["auction_state"]["bids"]}
    #     era_vals = auction_info["auction_state"]["era_validators"]
    #     cur_key_weights, cur_total_weight = _era_key_weights(era_vals[0]["validator_weights"])
    #     next_key_weights, next_total_weight = _era_key_weights(era_vals[1]["validator_weights"])
    #     error_node_ips = []
    #     for ip, node in nodes_status.items():
    #         if node.get("error", False):
    #             error_node_ips.append(ip)
    #             continue
    #         key = node.get("our_public_signing_key", None)
    #         node["cur_weight"] = cur_key_weights.get(key, 0)
    #         try:
    #             node["cur_percent"] = node["cur_weight"] / cur_total_weight
    #         except ZeroDivisionError:
    #             pass
    #         node["next_weight"] = next_key_weights.get(key, 0)
    #         try:
    #             node["next_percent"] = node["next_weight"] / next_total_weight
    #         except ZeroDivisionError:
    #             pass
    #         bid = key_bids.get(key)
    #         if bid is None:
    #             continue
    #         node["staked_amount"] = bid.get("staked_amount")
    #         node["delegation_rate"] = bid.get("delegation_rate")
    #         node["inactive"] = bid.get("inactive")
    #     FileSpider(network_name, config.WEB_DATA, nodes_status).save()


def generate_network_info(scheduler, network_config):
    print(f"Started: Generating info for network {network_config.name}.")
    start = time()
    ni = NetworkInfo(network_config)
    ni.generate()
    # look for a mid block time and schedule for next run
    # check for "fast mode".
    elapsed = round(time() - start, 1)
    print(f"Finished: Generating info for network {network_config.name}.  Runtime: {elapsed} secs.")


if __name__ == "__main__":
    generate_network_info(None, network_by_name("casper-test"))
