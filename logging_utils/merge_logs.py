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
                [<o1> <t3> <t4> <o2>],
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


@dataclass
class NeiryRecord:
    timestamp: int
    o1: float
    t3: float
    t4: float
    o2: float


@dataclass
class SpellerRecord:
    timestamp: int
    is_correct: bool


def read_bci_log(bci_file: str) -> list[NeiryRecord]:
    with open(bci_file, newline='') as bci_log:
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
        return [
            NeiryRecord(
                timestamp=int(record[0]),
                o1=float(record[1]),
                t3=float(record[2]),
                t4=float(record[3]),
                o2=float(record[4])
            ) for record in bci_log_reader
        ]


def read_speller_records(speller_file: str) -> list[SpellerRecord]:
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


def find_start_of_time_interval(bci_log: list[NeiryRecord], timestamp: int, start=0, end=-1) -> int:
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


def get_datapoint(bci_log: list[NeiryRecord], speller_record: SpellerRecord, shift: int, length: int) \
        -> dict[str, list[list[float]] | bool]:
    start_position: int = find_start_of_time_interval(bci_log=bci_log, timestamp=speller_record.timestamp)
    if start_position == -1:
        raise ValueError(
            'The bci log period and the speller log period do not overlap'
        )

    shifted_timestamp: int = bci_log[start_position].timestamp + shift
    shifted_position: int = find_start_of_time_interval(bci_log=bci_log, timestamp=shifted_timestamp,
                                                        start=start_position)
    if shifted_position == -1:
        raise ValueError(
            'The bci log period and the speller log period do not overlap'
        )

    end_position: int = shifted_position + length

    return {
        'is_correct': speller_record.is_correct,
        'bci': [
            [neiry_record.o1, neiry_record.t3, neiry_record.t4, neiry_record.o2]
            for neiry_record in bci_log[shifted_position:end_position]
        ]
    }


def combine_session_logs(bci_file: str, speller_file: str, shift: int, length: int) \
        -> list[dict[str, list[list[float]] | bool]]:
    bci_log: list[NeiryRecord] = read_bci_log(bci_file=bci_file)
    speller_log: list[SpellerRecord] = read_speller_records(speller_file=speller_file)
    return [
        get_datapoint(bci_log=bci_log, speller_record=speller_record, shift=shift, length=length)
        for speller_record in speller_log
    ]


def merge_logs(log_files: list[tuple[str, str]], output_file: str, shift: int, length: int, desc: str) -> None:
    unified_log: list[dict[str, list[list[float]] | bool]] = []
    for log_pair in log_files:
        single_session_combined_log: list[dict[str, list[list[float]] | bool]] = combine_session_logs(
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
        ('bci_v3/l3_01.csv', 'speller_v3/l3_01.csv'),
        ('bci_v3/l3_02.csv', 'speller_v3/l3_02.csv'),
        ('bci_v3/l3_03.csv', 'speller_v3/l3_03.csv'),
        ('bci_v3/l3_04.csv', 'speller_v3/l3_04.csv'),
        ('bci_v3/l3_05.csv', 'speller_v3/l3_05.csv'),
        ('bci_v3/l3_06.csv', 'speller_v3/l3_06.csv'),
        ('bci_v3/l3_07.csv', 'speller_v3/l3_07.csv'),
        ('bci_v3/l3_08.csv', 'speller_v3/l3_08.csv'),
        ('bci_v3/l3_09.csv', 'speller_v3/l3_09.csv'),
        ('bci_v3/l3_10.csv', 'speller_v3/l3_10.csv'),
        ('bci_v3/l3_11.csv', 'speller_v3/l3_11.csv'),
        ('bci_v3/l3_12.csv', 'speller_v3/l3_12.csv'),
        ('bci_v3/l3_13.csv', 'speller_v3/l3_13.csv'),
        ('bci_v3/l3_14.csv', 'speller_v3/l3_14.csv'),
        ('bci_v3/l3_14_1.csv', 'speller_v3/l3_14_1.csv'),
        ('bci_v3/l3_15.csv', 'speller_v3/l3_15.csv'),
        ('bci_v3/l3_16.csv', 'speller_v3/l3_16.csv'),
        ('bci_v3/l3_17.csv', 'speller_v3/l3_17.csv'),
    ]

    output_file: str = 'merged_log_v3.json'

    shift_milliseconds: int = 200  # Параметр для изменения
    duration_milliseconds: int = 300  # Параметр для изменения
    bci_records_per_second: int = 256
    length_records: int = bci_records_per_second * duration_milliseconds // 1000

    desc: str = f"""Все данные, собранные 2024-11-01.
Параметры bci: neiry, mono, filtered.
Параметры спеллера: speller v3, interval=100, interval_between_symbols=5000, interval_highlight=100.
Параметры объединения: shift={shift_milliseconds} мс, length={length_records} записей ({duration_milliseconds} мс)."""

    merge_logs(
        log_files=log_files,
        output_file=output_file,
        shift=shift_milliseconds,
        length=length_records,
        desc=desc
    )
