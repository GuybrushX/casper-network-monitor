from pathlib import Path

from .abstract_network_detail import AbstractNetworkDetail
from .pickle_util import save_bz2_pickle, load_bz2_pickle
from .file_utils import assure_dir_exists


class FileNetworkDetail(AbstractNetworkDetail):
    FILENAME = "network_detail.pbz2"

    def __init__(self, network_name: str, file_path: Path, node_details: dict = None):
        super().__init__(network_name, node_details)
        self._file_path = file_path

    @property
    def file_path(self) -> Path:
        return self._file_path / self.network_name / self.FILENAME

    def save(self):
        assure_dir_exists(self.file_path.parent)
        save_bz2_pickle(self._node_details, self.file_path)

    def load(self):
        self._node_details = load_bz2_pickle(self.file_path)
