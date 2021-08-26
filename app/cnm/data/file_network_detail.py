from pathlib import Path

from cnm.data.abstract_network_detail import AbstractNetworkDetail
from cnm.data.pickle_util import save_bz2_pickle, load_bz2_pickle
from cnm.data.file_utils import assure_dir_exists


class FileNetworkDetail(AbstractNetworkDetail):
    FILENAME = "network_detail.pbz2"

    def __init__(self, network_name: str, file_path: Path, node_details: dict = None):
        super().__init__(network_name, node_details)
        self.file_path = file_path

    @property
    def _file_path(self) -> Path:
        return self.file_path / self.network_name / self.FILENAME

    def save(self):
        assure_dir_exists(self._file_path.parent)
        save_bz2_pickle(self._node_details, self._file_path)

    def load(self):
        self._node_details = load_bz2_pickle(self._file_path)
