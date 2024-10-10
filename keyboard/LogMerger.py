import csv
import datetime
import os
import glob
from dataclasses import dataclass

@dataclass
class BCIRecord:
    timestamp: int
    o1: float
    t3: float
    t4: float
    o2: float

@dataclass
class SpellerPosition:
    row: int
    col: int

    def toString(self):
        return f"{self.row},{self.col}"

@dataclass
class SpellerRecord:
    timestamp: int
    position: SpellerPosition
    correct: bool

@dataclass
class DatasetRecord:
    o1: float
    t3: float
    t4: float
    o2: float
    position: SpellerPosition
    correct: bool

class LogMerger:
    def __init__(self, bci_log_path: str = None, speller_log_path: str = None, output_path: str = None):
        self.bci_log_path: str
        self.speller_log_path: str
        self.output_path: str

        self.bci_records: list[BCIRecord]
        self.speller_records: list[SpellerRecord]

        self.trimmed_bci_records: list[BCIRecord]
        self.trimmed_speller_records: list[SpellerRecord]

        self.dataset_records: list[DatasetRecord]

        self._set_filepaths(bci_log_path=bci_log_path,
                            gaze_tracker_log_path=speller_log_path,
                            output_path=output_path)
        self._read_bci_records()
        self._read_speller_records()
        self._generate_dateset_records()
        self._write_dataset_records()

    def _write_dataset_records(self):
        import pathlib
        pathlib.Path(self.output_path[0:self.output_path.rfind('/')]).mkdir(parents=True, exist_ok=True)
        with open(f'{self.output_path}.csv', 'w') as output_file:
            output_file.write('o1,t3,t4,o2,position,correct\n')
            for record in self.dataset_records:
                output_file.write(
                    f'{record.o1},{record.t3},{record.t4},{record.o2},'
                    f'{record.position.toString()},{str(record.correct)}\n'
                )

        with open(f'{self.output_path}_inputs.csv', 'w') as output_file:
            output_file.write('o1,t3,t4,o2\n')
            for record in self.dataset_records:
                output_file.write(f'{record.o1},{record.t3},{record.t4},{record.o2}\n')

        with open(f'{self.output_path}_values.csv', 'w') as output_file:
            output_file.write('direction_number\n')
            for record in self.dataset_records:
                output_file.write(
                    f'{record.position.toString()}\n'
                )

    def _generate_dateset_records(self):
        if len(self.bci_records) < 10:
            raise ValueError('The bci log is too short')
        if len(self.speller_records) < 10:
            raise ValueError('The speller log is too short')
        if (self.bci_records[1].timestamp > self.speller_records[-2].timestamp or
                self.bci_records[-2].timestamp < self.speller_records[1].timestamp):
            raise ValueError('The bci log period and the speller log period do not overlap')

        self._trim_records()

        #  TODO: clean up and optimise this mess
        self.dataset_records: list[DatasetRecord] = []
        trimmed_speller_records_last_index: int = len(self.trimmed_speller_records) - 1
        current_speller_record_index = 0
        for index, bci_record in enumerate(self.trimmed_bci_records):
            if (current_speller_record_index < trimmed_speller_records_last_index and
                    abs(bci_record.timestamp - self.speller_records[current_speller_record_index + 1].timestamp) <
                    abs(bci_record.timestamp - self.speller_records[current_speller_record_index].timestamp)):
                current_speller_record_index += 1

            current_speller_record = self.trimmed_speller_records[current_speller_record_index]
            self.dataset_records.append(DatasetRecord(
                o1=bci_record.o1,
                t3=bci_record.t3,
                t4=bci_record.t4,
                o2=bci_record.o2,
                position=current_speller_record.position,
                correct=current_speller_record.correct
            ))

    def _set_filepaths(self, bci_log_path, gaze_tracker_log_path, output_path):
        current_dir = os.path.dirname(__file__)

        self.bci_log_path = bci_log_path
        if self.bci_log_path is None:
            bci_logs = glob.glob(os.path.join(current_dir, '../logs/bci/*.csv'))
            self.bci_log_path = max(bci_logs, key=os.path.getctime)

        self.speller_log_path = gaze_tracker_log_path
        if self.speller_log_path is None:
            speller_logs = glob.glob(os.path.join(current_dir, '../logs/speller/*.csv'))
            self.speller_log_path = max(speller_logs, key=os.path.getctime)

        self.output_path = output_path
        if self.output_path is None:
            self.output_path = os.path.join(current_dir,
                                            f'../logs/datasets/{datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")}')

        if not os.path.isfile(self.bci_log_path):
            raise FileNotFoundError('Could not find the file with the BCI log')
        if not os.path.isfile(self.speller_log_path):
            raise FileNotFoundError('Could not find the file with the speller log')

    def _trim_records(self):
        first_bci_timestamp: int = self.bci_records[0].timestamp
        first_trimmed_speller_index: int = 0
        for index, webcam_record in enumerate(self.speller_records):
            if webcam_record.timestamp > first_bci_timestamp:
                first_trimmed_speller_index = index
                break

        last_bci_timestamp: int = self.bci_records[-1].timestamp
        last_trimmed_speller_index: int = 0
        for index, webcam_record in enumerate(reversed(self.speller_records)):
            if webcam_record.timestamp < last_bci_timestamp:
                last_trimmed_speller_index = len(self.speller_records) - index - 1
                break

        self.trimmed_speller_records: list[SpellerRecord] = self.speller_records[
                                                            first_trimmed_speller_index + 1:last_trimmed_speller_index - 1]

        #  TODO: replace with binary or interpolation search
        beginning_timestamp: int = (self.speller_records[first_trimmed_speller_index].timestamp
                                    + self.speller_records[first_trimmed_speller_index + 1].timestamp) // 2
        first_trimmed_bci_index: int = 0
        for index, bci_record in enumerate(self.bci_records):
            if bci_record.timestamp > beginning_timestamp:
                first_trimmed_bci_index = index
                break

        ending_timestamp: int = (self.speller_records[last_trimmed_speller_index].timestamp
                                 + self.speller_records[last_trimmed_speller_index - 1].timestamp) // 2
        last_trimmed_bci_index: int = 0
        for index, bci_record in enumerate(reversed(self.bci_records)):
            if bci_record.timestamp < ending_timestamp:
                last_trimmed_bci_index = len(self.bci_records) - index
                break

        self.trimmed_bci_records: list[BCIRecord] = self.bci_records[first_trimmed_bci_index:last_trimmed_bci_index]

        self.trimmed_webcam_records: list[SpellerRecord] = self.speller_records[
                                                           first_trimmed_speller_index:last_trimmed_speller_index]

    def _read_speller_records(self):
        with open(self.speller_log_path, newline='') as speller_log:
            speller_log_reader = csv.reader(speller_log, delimiter=',')
            header = next(speller_log_reader)
            if header[0] != 'timestamp' or header[1] != 'row' or header[2] != 'col' or header[3] != 'correct':
                raise ValueError(
                    '''The file with the gaze tracker log has wrong data formant. 
                    It must have a header with "timestamp", "row", "col" and "correct", 
                    separated by commas'''
                )
            self.speller_records = [
                SpellerRecord(
                    timestamp=int(record[0].replace(".", "")[:-1]),
                    position=SpellerPosition(
                        row=int(record[1]),
                        col=int(record[2])
                    ),
                    correct=bool(record[3])
                ) for record in speller_log_reader
            ]

    def _read_bci_records(self):
        with open(self.bci_log_path, newline='') as bci_log:
            bci_log_reader = csv.reader(bci_log, delimiter=',')
            header = next(bci_log_reader)
            if (header[0] != 'timestamp' or
                    (header[1] != 'O1' or header[2] != 'T3' or header[3] != 'T4' or header[4] != 'O2') and
                    (header[1] != 'channel_0' or header[2] != 'channel_1' or
                     header[3] != 'channel_2' or header[4] != 'channel_3')):
                raise ValueError(
                    '''The file with the BCI log has wrong data formant. 
                    It must have a header with "timestamp", "O1", "T3", "T4" and "O2", separated by commas'''
                )
            self.bci_records = [
                BCIRecord(
                    timestamp=int(record[0]),
                    o1=float(record[1]),
                    t3=float(record[2]),
                    t4=float(record[3]),
                    o2=float(record[4])
                ) for record in bci_log_reader
            ]


if __name__ == "__main__":
    bci_file = '.csv'
    speller_file = '.csv'
    output_file = 'merged_output.csv'

    LogMerger(bci_file, speller_file, output_file)
