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
        if header[2].split(':')[0].strip() != 'timestamp started':
            raise ValueError(
                '''This file doesn't have the starting timestamp at the expected place'''
            )
        timestamp_started: int = round(float(header[2].split(':')[1]))
        if header[3].split(':')[0].strip() != 'sampling':
            raise ValueError(
                '''This file doesn't have the sampling rate at the expected place'''
            )
        sampling: int = round(float(header[3].split(':')[1]))
        time_step: int = 1_000_000 // sampling
        corrected_log = [
            (
                timestamp_started + index * time_step,
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
                record[10],
                record[11],
                record[12],
                record[13],
                record[14],
                record[15],
            ) for index, record in enumerate(speller_log_reader)
        ]
    
    with open(log_file, mode='w', newline='') as corrected_log_file:
        writer = csv.writer(corrected_log_file)
        writer.writerow(["timestamp", "f3", "fc5", "af3", "f7", "t7", "p7", "o1", "o2", "p8", "t8", "f8", "af4", "fc6", "f4"])
        for record in corrected_log:
            writer.writerow(record)


if __name__ == "__main__":
    log_files: list[str] = [f'bci_logs/l4_{str(i).zfill(2)}.csv' for i in range(1, 18)]
    for log_file in log_files:
        correct_log(log_file)
