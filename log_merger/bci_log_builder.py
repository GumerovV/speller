import abc
from bci_data import BCISignalBatch, EmotivBatch, NeiryBatch, BCIRecord


class BciLogBuilder(abc.ABC):
    @abc.abstractmethod
    def are_headers_correct(self, headers: list[str]) -> bool:
        ...

    @abc.abstractmethod
    def read_values(self, values: list[str]) -> BCIRecord:
        ...


class NeiryLogBuilder(BciLogBuilder):
    def are_headers_correct(self, headers: list[str]) -> bool:
        if headers[0] != 'timestamp':
            return False
        if (headers[1].upper() == 'O1' 
            and headers[2].upper() == 'T3' 
            and headers[3].upper() == 'T4' 
            and headers[4].upper() == 'O2'
        ):
            return True
        for i in range(1, 5):
            if headers[i].upper() != f'CHANNEL_{i-1}':
                return False
        return True
    
    def read_values(self, values: list[str]) -> BCIRecord:
        batch: NeiryBatch = NeiryBatch(
            o1=float(values[1]),
            t3=float(values[2]),
            t4=float(values[3]),
            o2=float(values[4])
        )
        return BCIRecord(
            timestamp=int(values[0]),
            data=batch
        )



class EmotivLogBuilder(BciLogBuilder):
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

    def are_headers_correct(self, headers: list[str]) -> bool:
        if headers[0] != 'timestamp':
            return False
        if (headers[1].upper() == 'F3' #
            and headers[2].upper() == 'FC5' 
            and headers[3].upper() == 'AF3' #
            and headers[4].upper() == 'F7'
            and headers[5].upper() == 'T7' 
            and headers[6].upper() == 'P7' 
            and headers[7].upper() == 'O1'
            and headers[8].upper() == 'O2' 
            and headers[9].upper() == 'P8' 
            and headers[10].upper() == 'T8'
            and headers[11].upper() == 'F8'
            and headers[12].upper() == 'AF4' #
            and headers[13].upper() == 'FC6'
            and headers[14].upper() == 'F4' #
        ):
            return True
        return False
    
    def read_values(self, values: list[str]) -> BCIRecord:
        batch: EmotivBatch = EmotivBatch(
            f3=float(values[1]),
            fc5=float(values[2]),
            af3=float(values[3]),
            f7=float(values[4]),
            t7=float(values[5]),
            p7=float(values[6]),
            o1=float(values[7]),
            o2=float(values[8]),
            p8=float(values[9]),
            t8=float(values[10]),
            f8=float(values[11]),
            af4=float(values[12]),
            fc6=float(values[13]),
            f4=float(values[14])
        )
        return BCIRecord(
            timestamp=int(values[0]),
            data=batch
        )