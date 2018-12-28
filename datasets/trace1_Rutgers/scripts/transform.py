from typing import List, Tuple
from glob import glob
from os import makedirs, path
import multiprocessing as mp
import numpy as np
import pandas as pd

RUTGERS_SCRIPT_ROOT = path.dirname(path.abspath(__file__))
RUTGERS_ROOT = path.dirname(RUTGERS_SCRIPT_ROOT)
DATASETS_ROOT = path.dirname(RUTGERS_ROOT)
PROJECT_ROOT = path.dirname(DATASETS_ROOT)

RUTGERS_TRACES = path.join(RUTGERS_ROOT, 'data', '**', 'sdec*')

OUTPUT_DIR = path.join(PROJECT_ROOT, 'featureGenerator', 'datasets', 'dataset-2-rutgers_wifi')


def ensure_dir(file_path: str) -> None:
    directory = path.dirname(file_path)
    if not path.exists(directory):
        makedirs(directory)

    return file_path


def parse_rutgers(filename: str) -> pd.DataFrame:
    DTYPE = np.float32

    noise = int(filename.split('/')[-3][len('dbm'):])
    src = 'node' + filename.split('/')[-1][len('sdec'):]
    dst = filename.split('/')[-2].split('_')[1]

    data = np.full(shape=300, fill_value=np.NaN, dtype=DTYPE)
    with open(filename, 'r') as f:
        for line in f:
            d = line.split()
            if len(d) >= 2:
                seq, rssi = int(d[0]), int(d[1])
                if seq < 300 and rssi < 128 and rssi >= 0:
                    data[seq] = rssi

    df = pd.DataFrame(data=data, columns=['rssi'])
    df['seq'] = df.index + 1
    df['noise'] = noise
    df['src'] = src
    df['dst'] = dst
    df['received'] = ~df['rssi'].isnull()

    #df = df.set_index('seq')

    return df


def load_rutgers() -> List[pd.DataFrame]:
    """Will parse all traces. The output is list of Pandas DataFrame.

    Traces are not processed and contain missing fields
    """
    files = glob(RUTGERS_TRACES, recursive=True)
    traces = [parse_rutgers(df) for df in files]
    return traces


def load_rutgers_parallel() -> List[pd.DataFrame]:
    """Will parse all traces in parallel. The output is list/tuple of Pandas DataFrame.

    Traces are not processed and contain missing fields
    """
    files = glob(RUTGERS_TRACES, recursive=True)
    with mp.Pool() as p:
        traces = p.map(parse_rutgers, files)

    return traces


# Noise to experiment number mapping
# Just to comply with output directory name
if __name__ == '__main__':
    links = load_rutgers_parallel()
    for link in links:
        noise = link['noise'].values[0]
        src = link['src'].values[0]
        dst = link['dst'].values[0]
        link.to_csv(
            ensure_dir(f'{OUTPUT_DIR}/experiment-{abs(noise // 5) + 1}-noise_level_{abs(noise)}/{src}-{dst}-{noise}dBm.csv'),
            index=False,
            columns=['seq', 'src', 'dst', 'noise',  'received', 'rssi'],
        )


    print('Done!', len(links), 'traces')
