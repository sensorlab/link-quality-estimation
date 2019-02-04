import glob
import multiprocessing as mp
import sys
import hashlib
from os import path
from typing import Generator, Iterator, List, Tuple

import numpy as np
import pandas as pd

from collections import OrderedDict

from datasets.helpers import ensure_dir
from datasets.trace1_Rutgers import DATA_PATH, TRANSFORM_OUTPUT_PATH

TRACE_FILES = path.join(DATA_PATH, '**', 'sdec*')


dtypes = OrderedDict([
    ('seq', np.uint16),
    ('src', str),
    ('dst', str),
    ('noise', np.int8),
    ('received', np.bool),
    ('error', np.bool),
    ('rssi', np.uint8),
])

columns = list(dtypes.keys())


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

            assert len(row) == 2, 'Expected row length 2, got {}'.format(len(row))

            seq, _rssi_ = int(row[0]), np.uint8(row[1])

            if seq < 300:
            # Keep information about received packet
                if _rssi_ < 128 and _rssi_ >= 0:
                    rssi[seq] = _rssi_
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
    count = 0

    with mp.Pool() as pool:
        for _ in pool.imap(__write_traces__, get_traces()):
            count += 1

            # Print progress ...
            print(count, 'of 4060 links processed')
            sys.stdout.write('\033[F')

    print('Done!', count, 'links processed.')