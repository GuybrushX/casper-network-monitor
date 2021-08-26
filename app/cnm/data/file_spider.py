from pathlib import Path
from datetime import datetime
import shutil

from .abstract_spider import AbstractSpider
from .pickle_util import load_bz2_pickle, save_bz2_pickle


class FileSpider(AbstractSpider):

    def __init__(self, network_name: str, data_path: Path, nodes: dict = None):
        self._data_path = data_path / network_name
        self.nodes = nodes

    @property
    def _latest_file(self) -> Path:
        return self._data_path / "nodes_latest.pbz2"

    def save(self):
        nodes_file = self._data_path / "nodes" / f"nodes_{int(datetime.now().timestamp())}.pbz2"
        (self._data_path / "nodes").mkdir(parents=True, exist_ok=True)
        save_bz2_pickle(self.nodes, nodes_file)
        shutil.copy(nodes_file, self._latest_file)

    def load(self):
        self.nodes = load_bz2_pickle(self._latest_file)
