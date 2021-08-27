from pathlib import Path

from .abstract_network_summary import AbstractNetworkSummary
from .file_utils import assure_dir_exists
from .pickle_util import save_bz2_pickle, load_bz2_pickle


class FileNetworkSummary(AbstractNetworkSummary):
    FILENAME = "network_summary.pbz2"

    def __init__(self, network_name: str, file_path: Path, network_summary: dict = None):
        super().__init__(network_name, network_summary)
        self._file_path = file_path

    @property
    def file_path(self) -> Path:
        return self._file_path / self.network_name / self.FILENAME

    def save(self):
        assure_dir_exists(self.file_path.parent)
        save_bz2_pickle(self._network_summary, self.file_path)

    def load(self):
        self._network_summary = load_bz2_pickle(self.file_path)
