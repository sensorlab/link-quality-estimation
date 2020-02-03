import numpy as np
import matplotlib as mpl

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

np.random.seed(0x1234)
np.set_printoptions(precision=3)

from sklearn import ensemble, tree, model_selection, preprocessing, metrics, linear_model
from imblearn import over_sampling, under_sampling, pipeline, metrics as imetrics

from datasets.trace1_Rutgers.transform import get_traces as load_rutgers

from tools import (
    CustomInterpolation,
    SyntheticFeatures,
    CustomMerger,
    PRR,
    class_counter,
    norm_cm,
    set_styles,
    latexify, format_axes_for_cm, memory, ensure_dir
)

labels = ['good', 'interm.', 'bad']


def prr_to_label(prr: float) -> str:
    if prr >= 0.9:
        return 'good'
    elif prr <= 0.1:
        return 'bad'
    else:
        return 'interm.'


features = ['rssi', 'rssi_std', 'rssi_avg']

cv = model_selection.StratifiedKFold(n_splits=10, shuffle=True)

#classifier = ('logreg', linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr'))
classifier = ('dtree', tree.DecisionTreeClassifier())

pipe = pipeline.Pipeline([
    ('scaler', preprocessing.StandardScaler()),
    ('resample', over_sampling.RandomOverSampler()),
    classifier,
])


@memory.cache
def constant(pipe):
    print('*** ZERO PADDING interpolation ***')

    dataset = []
    for df in load_rutgers():
        df.loc[df['received'] == 0, 'rssi'] = np.nan
        dataset.append(df)
    print('Rutgers loaded ...')

    dataset = CustomInterpolation(source='rssi', strategy='constant', constant=0).fit_transform(dataset)
    print('Interpolation applied ...')

    dataset = SyntheticFeatures(source='rssi', window_size=10).fit_transform(dataset)
    print('Synthetic features created ...')

    dataset = PRR(source='received', window_size=10, ahead=1, target='prr').fit_transform(dataset)
    print('PRR created ...')

    dataset = CustomMerger().fit_transform(dataset)
    print('Datasets merged ...')

    dataset['class'] = dataset['prr'].apply(prr_to_label)
    print('Classification applied ...')

    dataset = dataset.dropna()

    X, y = dataset[features].copy(), dataset['class'].ravel()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    return y, y_pred


@memory.cache
def guassian(pipe):
    print('*** Gaussian interpolation ***')

    dataset = []
    for df in load_rutgers():
        df.loc[df['received'] == 0, 'rssi'] = np.nan
        dataset.append(df)
    print('Rutgers loaded ...')

    dataset = CustomInterpolation(source='rssi', strategy='gaussian').fit_transform(dataset)
    print('Interpolation applied ...')

    dataset = SyntheticFeatures(source='rssi', window_size=10).fit_transform(dataset)
    print('Synthetic features created ...')

    dataset = PRR(source='received', window_size=10, ahead=1, target='prr').fit_transform(dataset)
    print('PRR created ...')

    dataset = CustomMerger().fit_transform(dataset)
    print('Datasets merged ...')

    dataset['class'] = dataset['prr'].apply(prr_to_label)
    print('Classification applied ...')

    dataset = dataset.dropna()

    X, y = dataset[features].copy(), dataset['class'].ravel()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    return y, y_pred


@memory.cache
def without(pipe):
    print('*** Without interpolation ***')

    #dataset =load_rutgers(
    dataset = []
    for df in load_rutgers():
        df.loc[df['received'] == 0, 'rssi'] = np.nan
        df.dropna()
        dataset.append(df)

    print('Rutgers loaded ...')

    #dataset = CustomInterpolation(on_column='rssi', strategy='gaussian').fit_transform(dataset)
    #print('Interpolation applied ...')


    dataset = SyntheticFeatures(source='rssi', window_size=10).fit_transform(dataset)
    print('Synthetic features created ...')

    dataset = PRR(source='received', window_size=10, ahead=1, target='prr').fit_transform(dataset)
    print('PRR created ...')

    print('Apply discrete derivation (backward difference)')
    for i in range(len(dataset)):
        dataset[i]['drssi'] = dataset[i]['rssi'].diff()

    dataset = CustomMerger().fit_transform(dataset)
    print('Datasets merged ...')

    dataset['class'] = dataset['prr'].apply(prr_to_label)
    print('Classification applied ...')

    dataset = dataset.dropna()

    X, y = dataset[features].copy(), dataset['class'].ravel()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    return y, y_pred



def main():

    fig, axes = plt.subplots(1, 3, sharey=True, sharex=True)
    #fig.suptitle('Interpolation approaches')

    for ax, title, model in zip(axes.reshape(-1), ['Without', 'Gaussian', 'Constant', ], [without, guassian, constant, ]):
        y, y_pred = model()

        print(title, classifier[0])
        print(metrics.classification_report(y, y_pred, labels=labels))
        acc = metrics.accuracy_score(y, y_pred)
        cm = metrics.confusion_matrix(y, y_pred, labels=labels)
        cm = norm_cm(cm)

        cm = pd.DataFrame(cm, index=labels, columns=labels)
        sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
        ax.set_title(f'{title}\naccuracy={acc:.3f}')

    fig.tight_layout()
    fig.savefig('./different_interpolations.pdf', dpi=92, bbox_inches='tight')

    plt.show()


def multiple_figures():
    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])

    #width = 3.39
    #height = 3.39 * (np.sqrt(5) - 1.0) / 2.0
    latexify()


    for title, model in zip(['without', 'gaussian', 'constant', ], [without, guassian, constant, ]):
        y, y_pred = model(pipe)

        print(title, classifier[0])
        print(class_counter(y))
        print(metrics.classification_report(y, y_pred, labels=labels))


        acc = metrics.accuracy_score(y, y_pred)
        cm = metrics.confusion_matrix(y, y_pred, labels=labels)
        cm = norm_cm(cm)

        cm = pd.DataFrame(cm, index=labels, columns=labels)

        fig, ax = plt.subplots(dpi=92)

        sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
        format_axes_for_cm(ax)
        ax.set_title(f'accuracy = {acc:.3f}')

        fig.tight_layout()

        ensure_dir('./output/interpolations/')
        fig.savefig(f'./output/interpolations/{title}.pdf', dpi=92, bbox_inches='tight')
        plt.clf()
        #plt.close()

if __name__ == '__main__':
    #set_styles()
    #main()

    multiple_figures()
