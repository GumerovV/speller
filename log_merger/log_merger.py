"""
Объединяет несколько пар файлов, содержащих данные со спеллера и с BCI, в один json файл
Перебирает все записи со спеллера и сопоставляет каждой из них length записей, сделанных через
shift миллисекунд после них.

Основная функция - merge_logs(), остальные - вспомогательные.

В секции if __name__ == '__main__' приведён пример использования

Аргументы:
log_files: list[tuple[str, str]] - список пар путей к исходным файлам (сначала bci, потом спеллер)
output_file: str - путь к выходному файлу
shift: int - сдвиг окна (в миллисекундах) относительно появления стимула (подсветки)
length: int - длина окна (в записях)
desc: str - описание датасета (комментарий)

Пример выходного файла:
{
    'desc': 'описание датасета'
    'data': [
        {
            'is_correct': true,
            'bci': [
                [<o1> <t3> <t4> <o2> / <f3> <fc5> ... <f4>],
                ... length элементов
            ]
        },
        ...
    ]
}
"""

import csv
from dataclasses import dataclass
import json

from bci_data import BCIRecord
from bci_log_builder import BciLogBuilder, NeiryLogBuilder, EmotivLogBuilder


@dataclass
class SpellerRecord:
    timestamp: int
    is_correct: bool


class LogMerger:
    def __init__(self, bci_log_builder: BciLogBuilder) -> None:
        self.bci_log_builder: BciLogBuilder = bci_log_builder


    def _read_bci_log(self, bci_file: str) -> list[BCIRecord]:
        with open(bci_file, newline='') as bci_log:
            bci_log_reader = csv.reader(bci_log, delimiter=',')
            headers = next(bci_log_reader)
            if (not self.bci_log_builder.are_headers_correct(headers)):
                raise ValueError(
                    '''The file with the BCI log has incorrect headers'''
                )
            return [
                self.bci_log_builder.read_values(record)
                for record in bci_log_reader
            ]


    @staticmethod
    def _read_speller_records(speller_file: str) -> list[SpellerRecord]:
        with open(speller_file, newline='') as gaze_tracking_log:
            speller_log_reader = csv.reader(gaze_tracking_log, delimiter=',')
            header = next(speller_log_reader)
            if header[0] != 'timestamp' or header[1] != 'row' or header[2] != 'col' or header[3] != 'correct':
                raise ValueError(
                    '''The file with the speller log has wrong data formant. 
                    It must have a header with "timestamp", "row", "col" and "correct", 
                    separated by commas'''
                )
            return [
                SpellerRecord(
                    timestamp=int(record[0]),
                    is_correct=record[3] == 'True',
                ) for record in speller_log_reader
            ]


    @staticmethod
    def _find_start_of_time_interval(bci_log: list[BCIRecord], timestamp: int, start=0, end=-1) -> int:
        if start < 0 or start >= len(bci_log):
            start = 0
        if end < 0 or end >= len(bci_log):
            end = len(bci_log) - 1
        if timestamp < bci_log[start].timestamp:
            return 0
        if timestamp > bci_log[end].timestamp:
            return -1
        while end - start > 1:
            middle = (start + end) // 2
            if bci_log[middle].timestamp == timestamp:
                return middle
            elif bci_log[middle].timestamp < timestamp:
                start = middle
            else:
                end = middle
        return end


    @staticmethod
    def _get_datapoint(bci_log: list[BCIRecord], speller_record: SpellerRecord, shift: int, length: int) \
            -> dict[str, list[list[float]] | bool]:
        start_position: int = LogMerger._find_start_of_time_interval(bci_log=bci_log, timestamp=speller_record.timestamp)
        if start_position == -1:
            raise ValueError(
                'The bci log period and the speller log period do not overlap'
            )

        shifted_timestamp: int = bci_log[start_position].timestamp + shift
        shifted_position: int = LogMerger._find_start_of_time_interval(bci_log=bci_log, timestamp=shifted_timestamp,
                                                            start=start_position)
        if shifted_position == -1:
            raise ValueError(
                'The bci log period and the speller log period do not overlap'
            )

        end_position: int = shifted_position + length

        return {
            'is_correct': speller_record.is_correct,
            'bci': [
                bci_record.data.get_values()
                for bci_record in bci_log[shifted_position:end_position]
            ]
        }


    def _combine_session_logs(self, bci_file: str, speller_file: str, shift: int, length: int) \
            -> list[dict[str, list[list[float]] | bool]]:
        bci_log: list[BCIRecord] = self._read_bci_log(bci_file=bci_file)
        speller_log: list[SpellerRecord] = LogMerger._read_speller_records(speller_file=speller_file)
        return [
            LogMerger._get_datapoint(bci_log=bci_log, speller_record=speller_record, shift=shift, length=length)
            for speller_record in speller_log
    ]


    def merge_logs(self, log_files: list[tuple[str, str]], output_file: str, shift: int, length: int, desc: str) -> None:
        unified_log: list[dict[str, list[list[float]] | bool]] = []
        for log_pair in log_files:
            single_session_combined_log: list[dict[str, list[list[float]] | bool]] = self._combine_session_logs(
                bci_file=log_pair[0],
                speller_file=log_pair[1],
                shift=shift,
                length=length
            )
            unified_log.extend(single_session_combined_log)

        result = {
            'desc': desc,
            'data': list(unified_log)
        }

        with open(output_file, 'w') as fp:
            json.dump(result, fp)


if __name__ == '__main__':
    log_files: list[tuple[str, str]] = [
        (f'bci_logs/l4_{str(i).zfill(2)}.csv', f'speller_logs/l4_{str(i).zfill(2)}.csv')
        for i in range(1, 17)
    ]

    output_file: str = 'merged_log_emotiv_v3.json'

    shift_milliseconds: int = 200  # Параметр для изменения
    duration_milliseconds: int = 300  # Параметр для изменения
    bci_records_per_second: int = 128
    length_records: int = bci_records_per_second * duration_milliseconds // 1000

    desc: str = f"""Все данные, собранные 2024-11-09, кроме 16-й сессии.
Параметры bci: emotiv.
Параметры спеллера: speller v3, interval=200, interval_between_symbols=5000, interval_highlight=100.
Параметры объединения: shift={shift_milliseconds} мс, length={length_records} записей ({duration_milliseconds} мс)."""

    bci_log_builder: BciLogBuilder = EmotivLogBuilder()
    log_merger: LogMerger = LogMerger(bci_log_builder=bci_log_builder)
    log_merger.merge_logs(
        log_files=log_files,
        output_file=output_file,
        shift=shift_milliseconds,
        length=length_records,
        desc=desc
    )
