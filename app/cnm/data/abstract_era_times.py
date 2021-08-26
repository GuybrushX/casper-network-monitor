import abc
import datetime
import datetime as dt
import pytz

from .node_rpc import get_block, time_from_timestamp


class AbstractEraTimes(abc.ABC):
    DEFAULT_TIME_ZONES = ('UTC', 'US/Pacific', 'US/Eastern', 'Europe/Zurich', 'Asia/Hong_Kong')

    def __init__(self, network_config):
        self._config = network_config
        self.era_id = None
        self.era_start = None
        self.last_query = None
        self.next_query_time = None

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError

    def _get_block_era_height(self, block_height=None):
        block = get_block(self._config.rpc_url, block_height=block_height)
        return block, block["block"]["header"]["era_id"], block["block"]["header"]["height"]

    def from_rpc_query(self):
        block, cur_era, block_height = self._get_block_era_height(self._config.rpc_url)
        possible_era, last_block = cur_era, block
        while possible_era == cur_era:
            last_block = block
            block, possible_era, block_height = self._get_block_era_height(block_height=block_height - 1)
        era_start = time_from_timestamp(last_block["block"]["header"]["timestamp"])
        self.last_query = datetime.datetime.now()
        self.next_query_time = era_start + dt.timedelta(hours=2, minutes=4, seconds=9)
        self.era_id = cur_era
        self.era_start = era_start

    @staticmethod
    def _time_by_zone(date_time, zone):
        return pytz.timezone(zone).fromutc(date_time)

    def walk_forward(self, eras: int, time_zones: list = None):
        """
        Returns era_id, [(date_time, time_zone), ...]
        """
        if time_zones is None:
            time_zones = self.DEFAULT_TIME_ZONES
        era_time = self.era_start
        era_id = self.era_id
        while era_id < self.era_id + eras + 1:
            times = [(self._time_by_zone(era_time, zone), zone) for zone in time_zones]
            yield era_id, times
            era_time = era_time + dt.timedelta(hours=2, seconds=9)
            era_id += 1
