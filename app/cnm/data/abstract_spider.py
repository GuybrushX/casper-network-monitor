import abc


class AbstractSpider(abc.ABC):
    """ Abstract base class to hold data for a peer spider of a Casper network """

    @abc.abstractmethod
    def __init__(self, nodes: dict, network_name: str) -> 'AbstractSpider':
        raise NotImplementedError

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError
