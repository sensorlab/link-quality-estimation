import argparse
import glob
from os import path

import numpy as np
import pandas as pd

from datasets.helpers import interpolate_with_gaussian_noise
from datasets.trace1_Rutgers import TRANSFORM_OUTPUT_PATH

SUPPORTED_METHODS = ['constant', 'gaussian']


def guassian_interpolation() -> None:
    print(f'Applying "Gaussian" interpolation')
    filepaths = glob.iglob(
        path.join(TRANSFORM_OUTPUT_PATH, '**', '*.csv'), recursive=True)

    for filepath in filepaths:
        link = pd.read_csv(filepath)

        # Maybe some other interpolation was already applied. Clear it.
        link.loc[link.received == False, 'rssi'] = np.NaN

        # Replace invalid values with interpolation
        link['rssi'] = interpolate_with_gaussian_noise(link.rssi)
        link.to_csv(filepath, index=False)

    print(f'Processed {len(filepaths)} file(s)')


def constant_interpolation(const: int) -> None:
    print(f'Applying interpolation with constant {const}')
    filepaths = glob.iglob(
        path.join(TRANSFORM_OUTPUT_PATH, '**', '*.csv'), recursive=True)

    for filepath in filepaths:
        link = pd.read_csv(filepath)

        # Replace invalid values with interpolation
        link.loc[link.received == False, 'rssi'] = const

        # Save back to CSV
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

    print('Changes applied to:', TRANSFORM_OUTPUT_PATH)

    if args.method == 'constant':
        constant_interpolation(args.constant)

    if args.method == 'gaussian':
        guassian_interpolation()
