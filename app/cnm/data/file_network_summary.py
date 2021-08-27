from pathlib import Path

from .abstract_network_summary import AbstractNetworkSummary


class FileNetworkSummary(AbstractNetworkSummary):

    def __init__(self, network_name: str, file_path: Path, network_summary: dict):
        super().__init__(network_name)
        self._file_path = file_path
        self._network_summary = network_summary

    def save(self):
        pass

    def load(self):
        pass
