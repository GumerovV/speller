"""
Corrects timestamp format in speller logs, 
written before the #e8df74 commit
(decimal -> int without last digit)
"""


import csv


def correct_log(log_file: str):
    corrected_log = []
    with open(log_file, newline='') as speller_log:
        speller_log_reader = csv.reader(speller_log, delimiter=',')
        header = next(speller_log_reader)
        if header[0] != 'timestamp' or header[1] != 'row' or header[2] != 'col' or header[3] != 'correct':
            raise ValueError(
                '''The file with the gaze tracker log has wrong data formant. 
                It must have a header with "timestamp", "row", "col" and "correct", 
                separated by commas'''
            )
        corrected_log = [
            (
                int(float(record[0]) * 1_000_000),
                record[1],
                record[2],
                record[3],
            ) for record in speller_log_reader
        ]
    
    with open(log_file, mode='w', newline='') as corrected_log_file:
        writer = csv.writer(corrected_log_file)
        writer.writerow(["timestamp", "row", "col", "correct"])
        for record in corrected_log:
            writer.writerow(record)


if __name__ == "__main__":
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

    for pair in log_files:
        correct_log(pair[1])
