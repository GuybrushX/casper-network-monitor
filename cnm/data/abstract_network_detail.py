import abc
import operator


class AbstractNetworkDetail(abc.ABC):
    FIELDS = (0, 1, 3, 7, 17, 18, 16, 2, 21, 22, 9, 11, 6, 14)

    def __init__(self, network_name: str, node_details: dict = None):
        self._node_details: dict = node_details if node_details is not None else {}
        self.network_name: str = network_name

    @property
    def headers(self) -> list:
        return self._node_details.get("fields", [])

    @property
    def data(self) -> list:
        return self._node_details.get("data", [])

    @property
    def filtered_headers(self, indexes: list = None) -> list:
        if indexes is None:
            indexes = self.FIELDS
        # Approx 3 times faster than list comprehension
        return operator.itemgetter(*indexes)(self._node_details.get("fields", []))

    @property
    def filtered_data(self, indexes: list = None) -> list:
        if indexes is None:
            indexes = self.FIELDS
        # Approx 3 times faster than list comprehension
        f = operator.itemgetter(*indexes)
        return [f(data) for data in self._node_details.get("data", [])]

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError
