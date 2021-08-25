import mongoengine as me
import datetime
from ipaddress import ip_address

from node_rpc import time_from_timestamp


class LastAddedBlockInfo(me.EmbeddedDocument):
    hash = me.BinaryField(required=True)
    timestamp = me.DateTimeField(required=True)
    era_id = me.IntField(required=True)
    height = me.IntField(required=True)
    srh = me.BinaryField(required=True)
    creator = me.BinaryField(required=True)

    @staticmethod
    def from_dict(last_added_block_info: dict) -> 'LastAddedBlockInfo':
        """
                 "last_added_block_info": {"hash": "765a0c369b70e0dd3d657a18772d8b64c433bc5db3baa1dedb8356782bb5864f",
                                   "timestamp": "2021-08-16T02:01:13.472Z", "era_id": 1647, "height": 179267,
                                   "state_root_hash": "6b54752664e1c85b3240ac8ac4d41bf8285f6ab99d6325885b33f1e37d7613cb",
                                   "creator": "01b205c2bd03ce19cd2876ccc21a3566c407b631f3e714532ce0c9956bbac85811"},
        """
        return LastAddedBlockInfo(hash=bytes.fromhex(last_added_block_info["hash"]),
                                  timestamp=time_from_timestamp(last_added_block_info["timestamp"]),
                                  era_id=last_added_block_info["era_id"],
                                  height=last_added_block_info["height"],
                                  srh=bytes.fromhex(last_added_block_info["state_root_hash"]),
                                  creator=bytes.fromhex(last_added_block_info["creator"]))


class Status(me.EmbeddedDocument):
    """
    ip as int for space and speed
    """
    ip = me.IntField(required=True)
    api = me.StringField(required=True)
    name = me.StringField(required=True)
    ssrh = me.BinaryField(required=True)
    peers = me.ListField(me.IntField())
    labi = LastAddedBlockInfo(required=True)
    public_key = me.BinaryField(required=True)
    round_length = me.IntField()
    next_upgrade = me.DictField()
    build_ver = me.StringField()

    @staticmethod
    def _int_from_ip(ip_addr) -> int:
        return int(ip_address(ip_addr))

    @staticmethod
    def _peers_from_json(peers: list) -> list[int]:
        return [Status._int_from_ip(peer["address"].split(":")[0]) for peer in peers]

    @staticmethod
    def _secs_from_round_length(round_length: str):
        return 0
    #
    # d = {"api_version": "1.3.2", "chainspec_name": "casper",
    #      "starting_state_root_hash": "36068f8273ea797db7530305550d872a257e3891f606aeabccb452ff4bb23a7f",
    #      "peers": [{"node_id": "NodeId::Tls(0041..2aa5)", "address": "54.183.43.215:35000"},
    #                ],
    #      "last_added_block_info": {"hash": "765a0c369b70e0dd3d657a18772d8b64c433bc5db3baa1dedb8356782bb5864f",
    #                                "timestamp": "2021-08-16T02:01:13.472Z",
    #                                "era_id": 1647,
    #                                "height": 179267,
    #                                "state_root_hash": "6b54752664e1c85b3240ac8ac4d41bf8285f6ab99d6325885b33f1e37d7613cb",
    #                                "creator": "01b205c2bd03ce19cd2876ccc21a3566c407b631f3e714532ce0c9956bbac85811"},
    #      "our_public_signing_key": "0186d42bacf67a4b6c5042edba6bc736769171ca3320f7b0040ab9265aca13bbee",
    #      "round_length": None, "next_upgrade": None, "build_version": "1.3.2-e2027dbe9"}

    @staticmethod
    def from_status_dict(status: dict, ip: str) -> 'Status':
        Status(ip=int(ip_address(ip)),
               api=status["api_version"],
               name=status["chainspec_name"],
               ssrh=bytes.fromhex(status["starting_state_root_hash"]),
               peers=Status._peers_from_json(status["peers"]),
               labi=LastAddedBlockInfo.from_dict(status["last_added_block_info"]),
               public_key=bytes.fromhex(status["our_public_signing_key"]),
               round_length=Status._secs_from_round_length(status["round_length"]),
               next_upgrade=status["next_upgrade"],
               build_ver=status["build_version"])


class Spider(me.Document):
    """
    Holds spider of entire network including status endpoint data from all nodes in known_addresses
    """
    _id = me.ObjectIdField(primary_key=True)
    summary_id = me.ObjectIdField()
    network = me.StringField(required=True)
    update_timestamp = me.DateTimeField(required=True, default=datetime.datetime.now)
    statuses = me.ListField(Status())

    @staticmethod
    def from_network_query(peer_spider) -> 'Spider':
        pass


class SpiderSummary(me.Document):
    _id = me.ObjectIdField(primary_key=True)
    network = me.StringField(required=True)
    update_timestamp = me.DateTimeField(required=True, default=datetime.datetime.now)
    spider_id = me.ObjectIdField(required=True)
    versions = me.ListField(required=True)
    link_counts = me.ListField(required=True)

    @staticmethod
    def from_spider(spider) -> 'SpiderSummary':
        pass