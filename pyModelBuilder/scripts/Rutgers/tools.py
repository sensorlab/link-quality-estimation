import sys, os
from os import path, makedirs
from typing import Tuple, List
from collections import Counter
import multiprocessing as mp
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import itertools as it


from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import PolynomialFeatures

from joblib import Memory
CACHE_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), '.cache')
memory = Memory(CACHE_DIR, verbose=0)

TupleOrList = tuple([Tuple, List])

def interpolate_with_gaussian_noise(data: pd.Series) -> pd.Series:
    """Couldn't find a proper name. Very slow ..."""
    DTYPE = np.float32

    series = data.astype(DTYPE)
    values = series.tolist()
    processed = []

    series_size = len(values)

    prev_rssi = 0
    prev_seq = -1
    for seq, rssi in enumerate(values):
        if not np.isnan(rssi):
            avg_rssi = np.mean([prev_rssi, rssi])
            std_rssi = np.std([prev_rssi, rssi])
            std_rssi = std_rssi if std_rssi > 0 else np.nextafter(DTYPE(0), DTYPE(1))
            diff = seq - prev_seq - 1

            processed.extend(np.random.normal(avg_rssi, std_rssi, size=diff))
            processed.append(rssi)
            prev_seq, prev_rssi = seq, rssi

    avg_rssi = np.mean([prev_rssi, 0.])
    std_rssi = np.std([prev_rssi, 0.])
    diff = series_size - prev_seq - 1
    processed.extend(np.random.normal(avg_rssi, std_rssi, size=diff))

    series = pd.Series(data=processed, index=data.index, dtype=DTYPE)
    return series


def interpolate_with_constant(data: pd.Series, constant: int = 0) -> pd.Series:
    return data.fillna(value=constant)



def plot_cm(cm, labels: List, fmt='.2f', title='Confusion matrix'):
    """This function prints and plots the confusion matrix."""
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] # Normalize
    df = pd.DataFrame(cm, index=labels, columns=labels)

    ax = sns.heatmap(df, annot=True, square=True, fmt=fmt, vmax=1., vmin=0., cbar=False)
    ax.yaxis.set_ticklabels(ax.yaxis.get_ticklabels(), rotation=0, ha='right')
    ax.xaxis.set_ticklabels(ax.xaxis.get_ticklabels(), rotation=45, ha='right')
    ax.set_ylabel('True label')
    ax.set_xlabel('Predicted label')

    return ax

def class_counter(labels, normalize=True, ndigits=4) -> Counter:
    c = Counter(labels)
    if normalize:
        total = sum(c.values(), 0.0)
        for key in c:
            #c[key] /= total
            if ndigits:
                c[key] = round(c[key] / total, ndigits)
            else:
                c[key] /= total

    return c


def poly_features(df: pd.DataFrame, include: List[str], degree: int, include_bias=False, *args, **kwargs) -> pd.DataFrame:
    X, excluded = df.loc[:, include], df.drop(include, axis=1)
    poly = PolynomialFeatures(degree=degree, include_bias=include_bias, *args, **kwargs).fit(X)

    # Next line converts back to pandas, while preserving column names
    X = pd.DataFrame(poly.transform(X), columns=poly.get_feature_names(X.columns), index=X.index)

    data = pd.concat([X, excluded], axis=1, )
    data = data.reset_index(drop=True)

    # Transform column names. Ex. 'rssi rssi_avg' -> 'rssi*rssi_avg'
    data = data.rename(lambda cname: cname.replace(' ', '*'), axis='columns')

    return data


def feature_combinations(features: List[str]) -> List[List[str]]:
    """Generates combinations of features
    ex. [['rssi'], ['rssi_sd'], ['rssi_avg'], ['rssi', 'rssi_sd'], ... , ['rssi', 'rssi_avg', 'rssi_sd']]
    """
    combos = []
    for i in range(1, len(features)+1):
        for c in it.combinations(features, i):
            combos.append(c)

    return combos


def norm_cm(cm):
    return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]



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




class CustomInterpolation(BaseEstimator, TransformerMixin):
    """Possible strategies: ['gaussian', 'constant']"""

    STRATEGIES_ALL = ['gaussian', 'constant']

    def __init__(self, source:str, strategy:str='constant', constant:float=0, target=None):
        if strategy not in self.STRATEGIES_ALL:
            raise ValueError(f'"{strategy}" is not available strategy')

        self.strategy = strategy
        self.constant = constant

        self.source = source
        self.target = source if target is None else target


    def with_constant(self, data:pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[self.target] = df[self.source].fillna(value=self.constant)
        return df

    def with_gaussian(self, data:pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[self.target] = interpolate_with_gaussian_noise(df[self.source])
        return df

    def do_interpolation(self, X:pd.DataFrame) -> pd.DataFrame:
        if self.strategy == 'constant':
            return self.with_constant(X)

        if self.strategy == 'gaussian':
            return self.with_gaussian(X)

        raise ValueError(f'"{self.strategy}" is not available strategy')

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X, y='deprecated', copy=True):
        if isinstance(X, (List, Tuple, )):
            with mp.Pool() as p:
                return p.map(self.do_interpolation, X)

        return self.do_interpolation(X)


class SyntheticFeatures(BaseEstimator, TransformerMixin):
    """Rolling window for mean & std features."""

    def __init__(self, source:str, window_size:int=10, target=None):
        self.source = source
        self.target = source if target is None else target

        if not isinstance(window_size, int) or not window_size > 0:
            raise ValueError(f'Window should be positive integer. Got `{window_size}` instead.')

        self.window = window_size

    def fit(self, X, y=None):
        return self

    def do_synthetics(self, data:pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df[f'{self.target}_avg'] = df[self.source].rolling(self.window).mean()
        df[f'{self.target}_std'] = df[self.source].rolling(self.window).std()
        return df


    def transform(self, X: pd.DataFrame, y='deprecated', copy=True):
        if isinstance(X, (List, Tuple, )):
            with mp.Pool() as p:
                return p.map(self.do_synthetics, X)

        return self.do_synthetics(X)


class PRR(BaseEstimator, TransformerMixin):
    """Calculate PRR based on `target`"""

    def __init__(self, source:str, window_size:int, ahead:int, target:str='prr'):
        self.source = source
        self.target = source if target is None else target

        if not isinstance(window_size, int) or not window_size > 0:
            raise ValueError(f'window_size should be positive integer. Got `{window_size}` instead.')

        self.window = window_size

        if not isinstance(ahead, int) or not ahead >= 0:
            raise ValueError(f'ahead should be greater or equal to zero integer. Got `{ahead}` instead.')

        self.ahead = ahead

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def calculate_prr(self, dataframe):
        df = dataframe.copy()
        df[self.target] = (df[self.source].astype(bool).rolling(self.window).sum() / self.window).shift(-1 * self.window * self.ahead)
        return df

    def transform(self, X: pd.DataFrame, y='deprecated'):
        if isinstance(X, TupleOrList):
            with mp.Pool() as p:
                return p.map(self.calculate_prr, X)

        return self.calculate_prr(X)


class CustomMerger(BaseEstimator, TransformerMixin):
    """Merge List of DataFrames"""

    def __init__(self):
        pass

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame, y='deprecated', copy=True):
        if isinstance(X, TupleOrList):
            return pd.concat(X, ignore_index=True).reset_index(drop=True)

        return X


class CustomSplitter(BaseEstimator, TransformerMixin):
        def __init__(self, X:TupleOrList=None, y:str='class', drop:TupleOrList=None):
            self.X = X
            self.y = y
            self.drop = drop

        def fit(self, X:pd.DataFrame, y=None):
            return self

        def transform(self, df: pd.DataFrame, y='deprecated', copy=True):
            df = df.copy() if copy else df
            if self.drop:
                df.drop(labels=self.drop, axis=1, inplace=True)

            if self.X:
                return df[self.X], df[self.y].ravel()

            return df.drop(self.y), df[self.y].ravel()



def set_styles():
    #mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])
    sns.set(context='paper', style='white', palette='Greys', font='sans-serif', color_codes=True)

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

def ensure_dir(file_path):
    directory = path.dirname(file_path)
    if not path.exists(directory):
        makedirs(directory)
