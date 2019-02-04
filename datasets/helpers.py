from os import path, makedirs

import numpy as np
import pandas as pd

import matplotlib as mpl
import seaborn as sns

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



def format_axes_for_chart(ax: mpl.axis.Axis) -> mpl.axis.Axis:
    SPINE_COLOR = 'gray'

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(SPINE_COLOR)
        ax.spines[spine].set_linewidth(0.5)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction='out', color=SPINE_COLOR)

    return ax

def format_axes_for_cm(ax: mpl.axis.Axis) -> mpl.axis.Axis:
    SPINE_COLOR = 'gray'

    for _, spine in ax.spines.items():
        spine.set_visible(True)
        spine.set_color(SPINE_COLOR)
        spine.set_linewidth(0.5)

    return ax


def set_styles():
    #mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])
    sns.set(context='paper', style='white', palette='Greys', font='sans-serif', color_codes=True, rc={
        'figure.dpi': 92,
    })


def latexify(fig_width:float=None, fig_height:float=None, columns:int=1) -> None:
    """Set up matplotlib's RC params for LaTeX plotting. Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert(columns in [1,2])

    if fig_width is None:
        fig_width = 3.39 if columns==1 else 6.9 # width in inches

    if fig_height is None:
        golden_mean = (np.sqrt(5) - 1.0) / 2.0    # Aesthetic ratio
        fig_height = fig_width * golden_mean # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height +
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {
        #'backend': 'ps',
        #'text.latex.preamble': ['\usepackage{gensymb}'],
        #'axes.labelsize': 8, # fontsize for x and y labels (was 10)
        #'axes.titlesize': 8,
        #'text.fontsize': 8, # was 10
        #'legend.fontsize': 8, # was 10
        #'xtick.labelsize': 8,
        #'ytick.labelsize': 8,
        #'text.usetex': True,
        'figure.figsize': [fig_width,fig_height],
        #'font.family': 'serif'
    }

    mpl.rcParams.update(params)
