import abc
from dataclasses import dataclass


class BciSignalBatch(abc.ABC):
    @abc.abstractmethod
    def get_headers(self) -> list[str]:
        ...

    @abc.abstractmethod
    def get_values(self) -> list[float]:
        ...


@dataclass
class NeiryBatch(BciSignalBatch):
    o1: float
    t3: float
    t4: float
    o2: float

    def get_headers(self) -> list[str]:
        return ['o1','t3','t4','o2']

    def get_values(self) -> list[float]:
        return [self.o1, self.t3, self.t4, self.o2]


@dataclass
class EmotivBatch(BciSignalBatch):
    f3: float
    fc5: float
    af3: float
    f7: float
    t7: float
    p7: float
    o1: float
    o2: float
    p8: float
    t8: float
    f8: float
    af4: float
    fc6: float
    f4: float

    def get_headers(self) ->list[str]:
        return ['f3','fc5','af3','f7','t7','p7','o1','o2','p8','t8','f8','af4','fc6','f4']

    def get_values(self) -> list[float]:
        return [self.f3, self.fc5, self.af3, self.f7, self.t7, self.p7, self.o1, self.o2, self.p8, self.t8, self.f8, self.af4, self.fc6, self.f4]


@dataclass
class BciRecord:
    timestamp: int
    data: BciSignalBatch