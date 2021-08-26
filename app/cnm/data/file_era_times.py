from pathlib import Path
import json
import datetime as dt

from .abstract_era_times import AbstractEraTimes
from .file_utils import assure_dir_exists


class FileEraTimes(AbstractEraTimes):

    def __init__(self, network_config, data_path: Path):
        super().__init__(network_config)
        self._data_path = data_path

    @property
    def _file_path(self) -> Path:
        return self._data_path / self._config.name / "era_times.json"

    def save(self):
        assure_dir_exists(self._file_path.parent)
        data = json.dumps({"era_id": self.era_id,
                           "era_start": self.era_start.timestamp(),
                           "last_query": self.last_query.timestamp(),
                           "next_query_time": self.next_query_time.timestamp()})
        self._file_path.write_text(data)

    def load(self):
        data = json.loads(self._file_path.read_text())
        self.era_id = data.get("era_id")
        self.era_start = dt.datetime.utcfromtimestamp(data.get("era_start"))
        self.last_query = dt.datetime.utcfromtimestamp(data.get("last_query"))
        self.next_query_time = dt.datetime.utcfromtimestamp(data.get("next_query_time"))
