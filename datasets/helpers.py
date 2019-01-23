from os import path, makedirs

import numpy as np
import pandas as pd

def ensure_dir(file_path: str) -> str:
    """Function will ensure that directories to file exists. Input is forwarded to output."""
    directory = path.dirname(file_path)
    if not path.exists(directory):
        makedirs(directory)

    return file_path



def interpolate_with_gaussian_noise(series: pd.Series, dtype=np.float32) -> pd.Series:
    """Fill gaps of NaN(s) with gaussian distribution of previous and next valid value."""

    series = series.astype(dtype) # convert datatype
    values = series.tolist()
    processed = []

    series_size = len(values)

    prev_rssi = 0
    prev_seq = -1
    for seq, rssi in enumerate(values):
        if not np.isnan(rssi):
            avg_rssi = np.mean([prev_rssi, rssi])
            std_rssi = np.std([prev_rssi, rssi])
            std_rssi = std_rssi if std_rssi > 0 else np.nextafter(dtype(0), dtype(1))
            diff = seq - prev_seq - 1

            processed.extend(np.random.normal(avg_rssi, std_rssi, size=diff))
            processed.append(rssi)
            prev_seq, prev_rssi = seq, rssi

    avg_rssi = np.mean([prev_rssi, 0.])
    std_rssi = np.std([prev_rssi, 0.])
    diff = series_size - prev_seq - 1
    processed.extend(np.random.normal(avg_rssi, std_rssi, size=diff))

    series = pd.Series(data=processed, index=series.index, dtype=dtype)
    return series
