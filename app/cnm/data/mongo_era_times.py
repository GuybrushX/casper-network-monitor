import datetime as dt
import pytz
from abstract_era_times import AbstractEraTimes
import mongoengine as me

from node_rpc import get_block, time_from_timestamp

DEFAULT_TIME_ZONES = ('UTC', 'US/Pacific', 'US/Eastern', 'Europe/Zurich', 'Asia/Hong_Kong', 'Australia/Sydney')


class _MongoEraTimes(me.document):
    _id = me.StringField(required=True, primary_key=True)
    era_id = me.IntField(required=True)
    era_start = me.DateTimeField(required=True)
    last_query = me.DateTimeField()
    next_query_time = me.DateTimeField()


class MongoEraTimes(AbstractEraTimes):

    def __init__(self, network_config):
        super().__init__(network_config)
        raise NotImplementedError("Need db connection")

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError
