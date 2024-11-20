import abc
from bci_data import BciSignalBatch
import random


class BciClassifier(abc.ABC):
    @abc.abstractmethod
    def classifiy(self, data: list[BciSignalBatch]) -> float:
        ...

class RandomClassifier(BciClassifier):
    def classifiy(self, data: list[BciSignalBatch]) -> float:
        return random.random()