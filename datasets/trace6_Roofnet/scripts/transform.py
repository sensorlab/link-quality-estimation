#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import glob
from shutil import rmtree
import numpy as np
import pandas as pd
from os import path


ROOT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
DATA_DIR = path.join(ROOT_DIR, 'data')

#OUTPUT_FILE = path.join(ROOT_DIR, 'roofnet')
OUTPUT_DIR = path.abspath(
    path.join(ROOT_DIR, '../../featureGenerator/datasets/dataset-6-roofnet/')
)

# Optimal datatypes for reducing data footprint
dtypes = {
    'exp_id': np.uint64,
    'link_test': np.uint32,
    'test_phase': np.int32,
    'src': np.uint16,
    'dst': np.uint16,
    'seq': np.uint64,
    'time': np.float32,
    'signal': np.uint8,
    'noise': np.uint8,
    'bitrate': np.float32,
}


def process_data():
    if path.exists(OUTPUT_DIR):
        rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR)

    SEARCH = path.abspath(path.join(DATA_DIR, './**/*.csv'))
    for filepath in glob.glob(SEARCH, recursive=True):
        filename = filepath.split('/')[-1]

        # extract info from filename
        filename, ext = path.splitext(filename)
        src, dst, bitrate = filename.split('-')


        df = pd.read_csv(filepath)
        df['bitrate'] = float(bitrate)

        # assumption that SNR < 10 leads to packet loss
        df['received'] = (df['signal'] - df['noise']) >= 10

        # Reduce size
        df = df.astype(dtypes)

        # Drop unused columns
        #df = df.drop(['exp_id', 'link_test', 'test_phase', 'src', 'dst', 'bitrate'], axis=1)

        output_file = path.join(OUTPUT_DIR, f'{src}-{dst}-{bitrate}.csv')
        df.to_csv(output_file, index=False, columns=['seq', 'time', 'signal', 'noise', 'received'])


if __name__ == '__main__':
    process_data()

