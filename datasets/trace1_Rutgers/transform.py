import glob
import multiprocessing as mp
import sys
import hashlib
from os import path
from typing import Generator, Iterator, List, Tuple

import numpy as np
import pandas as pd

from tqdm import tqdm

from collections import OrderedDict

from datasets.helpers import ensure_dir
from datasets.trace1_Rutgers import DATA_PATH, TRANSFORM_OUTPUT_PATH

TRACE_FILES = path.join(DATA_PATH, '**', 'sdec*')


dtypes = OrderedDict([
    ('seq', np.uint16),
    ('src', str),
    ('dst', str),
    ('noise', np.int8),
    ('received', bool),
    ('error', bool),
    ('rssi', np.uint8),
])

columns = list(dtypes.keys())


def get_filenames() -> List[str]:
    """Returns iterator, which iterates through file paths of all Rutgers link traces."""
    filenames = glob.glob(TRACE_FILES, recursive=True)
    assert len(filenames) != 0
    return filenames


def parser(filename: str) -> pd.DataFrame:
    """Returns Pandas DataFrame produced from reading and parsing specified Rutgers link trace."""
    # datasets/trace1_Rutgers/data/dbm-5/Results_node1-4_DailyTest_Sat-Oct-15-03_54_00-2005/sdec1-2
    # node1-4 is Tx node, while sdec1-2 is Rx node in our case

    noise = np.int8(filename.split('/')[-3][len('dbm'):])
    tx = filename.split('/')[-2].split('_')[1]
    rx = 'node' + filename.split('/')[-1][len('sdec'):]

    rssi = np.full(shape=300, fill_value=0, dtype=np.uint8)
    received = np.full(shape=300, fill_value=False, dtype=bool)
    error = np.full(shape=300, fill_value=False, dtype=bool)

    with open(filename, mode='r') as file:
        for line in file:
            row = line.split()

            assert len(row) == 2, 'Expected row length 2, got {}'.format(len(row))

            seq, value = int(row[0]), np.uint8(row[1])

            if seq < 300:
                # Keep information about received packet
                if value < 128 and value >= 0:
                    rssi[seq] = value
                    received[seq] = True

                else:
                    # Keep information if RSSI was invalid
                    #rssi[seq] = 0
                    error[seq] = True

    df = pd.DataFrame(
        data={
            'rssi': rssi,
            'received': received,
            'error': error,
        }
    )

    df['seq'] = df.index + 1
    df['noise'] = noise
    df['src'] = tx
    df['dst'] = rx

    # Convert to appropriate types
    df = df.astype(dtypes)

    return df


def get_traces() -> Iterator[pd.DataFrame]:
    """Returns generator of DataFrames."""
    with mp.Pool() as pool:
        for df in pool.imap(parser, get_filenames()):
            yield df


def get_traces2(n_jobs=None) -> List[pd.DataFrame]:
    from joblib import delayed, Parallel
    filenames = get_filenames()

    output = Parallel(n_jobs=n_jobs)(delayed(parser)(filename) for filename in filenames)
    assert len(output) != 0
    return output


def __write_traces__(link: pd.DataFrame) -> None:
    sha1 = hashlib.sha256(
        link.values.tobytes()
    ).hexdigest()

    output_path = path.join(
        TRANSFORM_OUTPUT_PATH,
        '{}.csv'.format(sha1),
    )

    assert path.isfile(output_path) == False, 'Filename collision!'

    link.to_csv(
        ensure_dir(output_path),
        index=False,
        columns=columns,
    )


if __name__ == '__main__':
    """This executes if and only if this Python script is called directly."""

    with mp.Pool() as pool:
        for _ in tqdm(pool.imap(__write_traces__, get_traces()), unit=' traces'):
            pass
