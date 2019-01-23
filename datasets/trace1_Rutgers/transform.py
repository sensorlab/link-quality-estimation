import glob
import multiprocessing as mp
from os import makedirs, path
from typing import Generator, Iterator, List, Tuple

from datasets.trace1_Rutgers import DATA_PATH, TRANSFORM_OUTPUT_PATH
from datasets.helpers import ensure_dir

import numpy as np
import pandas as pd


TRACE_FILES = path.join(DATA_PATH, '**', 'sdec*')


dtypes = {
    'rssi': np.uint8,
    'received': np.bool,
    'error': np.bool,
    'seq': np.uint16,
    'noise': np.int8,
}


def get_filenames() -> Iterator[str]:
    """Returns iterator, which iterates through file paths of all Rutgers link traces."""
    return glob.iglob(TRACE_FILES, recursive=True)


def parser(filename: str) -> pd.DataFrame:
    """Returns Pandas DataFrame produced from reading and parsing specified Rutgers link trace."""
    # datasets/trace1_Rutgers/data/dbm-5/Results_node1-4_DailyTest_Sat-Oct-15-03_54_00-2005/sdec1-2
    noise = np.int8(filename.split('/')[-3][len('dbm'):])
    src = filename.split('/')[-2].split('_')[1]
    dst = 'node' + filename.split('/')[-1][len('sdec'):]

    rssi = np.full(shape=300, fill_value=0, dtype=np.uint8)
    received = np.full(shape=300, fill_value=False, dtype=np.bool)
    error = np.full(shape=300, fill_value=False, dtype=np.bool)

    with open(filename, mode='r') as file:
        for line in file:
            row = line.split()

            assert len(row) == 2, f'Expected row length 2, got {len(row)}'

            seq, _rssi_ = np.uint8(row[0]), np.uint8(row[1])

            # Keep information about received packet
            if seq < 300 and _rssi_ < 128 and _rssi_ >= 0:
                rssi[seq] = _rssi_
                received[seq] = True
                continue

            # Keep information if RSSI was invalid
            if seq < 300 and _rssi_ == 128:
                rssi[seq] = 0
                error[seq] = True
                continue

    df = pd.DataFrame(
        data={
            'rssi': rssi,
            'received': received,
            'error': error,
        }
    )

    df['seq'] = df.index + 1
    df['noise'] = noise
    df['src'] = src
    df['dst'] = dst

    # Convert to appropriate types
    df = df.astype(dtypes)

    return df


def get_traces() -> Iterator[pd.DataFrame]:
    """Returns generator of DataFrames."""
    with mp.Pool() as pool:
        for df in pool.imap(parser, get_filenames()):
            yield df


if __name__ == '__main__':
    """This executes if and only if this Python script is called directly."""
    count = 0
    for link in get_traces():
        noise = link.noise.values[0]
        src = link.src.values[0]
        dst = link.dst.values[0]

        col_order = ['seq', 'src', 'dst', 'noise', 'received', 'rssi', 'error']
        output_path = f'{TRANSFORM_OUTPUT_PATH}/experiment-{abs(noise // 5) + 1}-noise_level_{abs(noise)}/{src}-{dst}-{noise}dBm.csv'

        link.to_csv(
            ensure_dir(output_path),
            index=False,
            columns=col_order,
        )

        count += 1

    print(f'Processed {count} files!')
