import abc


class AbstractNetworkSummary(abc.ABC):

    def __init__(self, network_name: str, network_summary: dict = None):
        self._network_summary: dict = network_summary if network_summary is not None else {}
        self.network_name: str = network_name

    def full_summary(self):
        return self._network_summary.get("full", {})

    def top_summary(self):
        return self._network_summary.get("top", {})

    def full_links(self):
        return self._network_summary.get("full_links", {})

    def top_links(self):
        return self._network_summary.get("top_links", {})

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError
