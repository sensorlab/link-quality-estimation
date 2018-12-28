import sys, os
from os import path, makedirs

"""
Because of intentional limitation of the Python, dependencies can be imported
from parent directory, but not from parent of parent, unless it is in sys.path.
"""
from transform import OUTPUT_DIR, ensure_dir, PROJECT_ROOT

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

directory = path.join(PROJECT_ROOT, 'pyModelBuilder')
if directory not in sys.path:
    sys.path.insert(0, directory)

directory = path.join(PROJECT_ROOT, 'pyModelBuilder', 'scripts')
if directory not in sys.path:
    sys.path.insert(0, directory)


from pyModelBuilder.scripts.tools import interpolate_with_gaussian_noise


from glob import glob
import multiprocessing as mp
from os import mkdir, path
from typing import List
import argparse

import numpy as np
import pandas as pd


SUPPORTED_METHODS = ['constant', 'gaussian']


def guassian_interpolation():
    print(f'Applying "Gaussian" interpolation')
    filepaths = glob(path.join(OUTPUT_DIR, '**', '*.csv'), recursive=True)

    for filepath in filepaths:
        link = pd.read_csv(filepath)

        # Maybe some other interpolation was already applied. Clear it.
        link['rssi'] = link['rssi'].where(link.received)

        # Replace invalid values with interpolation
        link['rssi'] = interpolate_with_gaussian_noise(link.rssi)
        link.to_csv(filepath, index=False)

    print(f'Processed {len(filepaths)} file(s)')


def constant_interpolation(const: int):
    print(f'Applying interpolation with constant {const}')
    filepaths = glob(path.join(OUTPUT_DIR, '**', '*.csv'), recursive=True)


    for filepath in filepaths:
        link = pd.read_csv(filepath)

        # Maybe some other interpolation was already applied. Clear it.
        link.rssi = link.rssi.where(link.received)

        # Replace invalid values with interpolation
        link.rssi = link.rssi.replace([np.inf, -np.inf, np.nan], const)
        link.to_csv(filepath, index=False)

    print(f'Processed {len(filepaths)} file(s)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interpolate Rutgers dataset')
    parser.add_argument(
        '-m', '--method',
        metavar='METHOD',
        type=str,
        dest='method',
        required=True,
        choices=SUPPORTED_METHODS,
        help='Interpolate link data (options: constant|gaussian)',
    )

    parser.add_argument(
        '-c',
        metavar='NUMBER',
        type=float,
        dest='constant',
        default=0.,
        help='(-m `constant` only) replacement value (default: 0)'
    )

    args = parser.parse_args()

    print(OUTPUT_DIR)

    if args.method == 'constant':
        constant_interpolation(args.constant)

    if args.method == 'gaussian':
        guassian_interpolation()
