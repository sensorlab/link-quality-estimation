from collections import Counter
import numpy as np
import matplotlib as mpl

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

np.random.seed(0x1234)
np.set_printoptions(precision=3)

from sklearn import ensemble, tree, model_selection, preprocessing, metrics, linear_model
from imblearn import over_sampling, under_sampling, pipeline, metrics as imetrics


import datasets
from datasets.trace1_Rutgers.transform import get_traces


from tools import (
    CustomInterpolation,
    SyntheticFeatures,
    CustomMerger,
    PRR,
    class_counter,
    norm_cm,
    set_styles,
    memory,
    format_axes_for_cm,
    latexify,
    ensure_dir
)

labels = ['good', 'interm.', 'bad']

@memory.cache
def load_rutgers():
    return list(get_traces())


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

@memory.cache
def prepare_data():
    dataset = load_rutgers()
    print('Rutgers loaded ...')

    dataset = CustomInterpolation(source='rssi', strategy='constant', constant=0).fit_transform(dataset)
    print('Interpolation applied ...')

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

    return X, y


@memory.cache
def no_resample(classifier):
    print('*** NO RESAMPLE ***')

    pipe = pipeline.Pipeline([
        ('scaler', preprocessing.StandardScaler()),
        classifier,
    ])

    X, y = prepare_data()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    c = Counter(y)

    return y, y_pred, c




@memory.cache
def oversample(classifier):
    print('*** OVERSAMPLE ***')

    pipe = pipeline.Pipeline([
        ('scaler', preprocessing.StandardScaler()),
        ('resample', over_sampling.RandomOverSampler()),
        classifier,
    ])

    X, y = prepare_data()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    c = Counter(over_sampling.RandomOverSampler().fit_sample(X, y)[1])

    return y, y_pred, c


@memory.cache
def undersample(classifier):
    print('*** UNDERSAMPLE ***')

    pipe = pipeline.Pipeline([
        ('scaler', preprocessing.StandardScaler()),
        ('resample', under_sampling.RandomUnderSampler()),
        classifier,
    ])

    X, y = prepare_data()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    c = Counter(under_sampling.RandomUnderSampler().fit_sample(X, y)[1])

    return y, y_pred, c



def main():
    fig, axes = plt.subplots(1, 3, sharey=True, sharex=True)
    #fig.suptitle('Resample approaches')

    for ax, title, model in zip(axes.flat, ['No resample', 'Oversample', 'Undersample', ], [no_resample, oversample, undersample]):
        y, y_pred, c = model()

        print(title)
        print(imetrics.classification_report_imbalanced(y, y_pred))

        acc = metrics.accuracy_score(y, y_pred)
        cm = metrics.confusion_matrix(y, y_pred, labels=labels)
        cm = norm_cm(cm)

        cm = pd.DataFrame(cm, index=labels, columns=labels)
        sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
        ax.set_title(f'{title}\naccuracy={acc:.3f}')


    count = class_counter(y)
    fig.suptitle('Population: ' + ', '.join([f'{key}: {count[key]*100:.1f}%' for key in labels]))

    fig.tight_layout()
    fig.savefig('./different_resampling.pdf', dpi=92, bbox_inches='tight')

    plt.show()


def multiplots():
    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])

    latexify()

    for model, title in zip([no_resample, undersample, oversample], ['none', 'undersample', 'oversample']):
        y, y_pred, c = model(classifier)

        acc = metrics.accuracy_score(y, y_pred)
        #prec = metrics.precision_score(y, y_pred, labels=labels, average='macro')
        #rec = metrics.recall_score(y, y_pred, labels=labels, average='macro')
        #f1 = metrics.f1_score(y, y_pred, labels=labels, average='macro')

        cm = metrics.confusion_matrix(y, y_pred, labels=labels)
        cm = norm_cm(cm)

        cm = pd.DataFrame(cm, index=labels, columns=labels)

        fig, ax = plt.subplots(dpi=92, constrained_layout=True)
        #print(f'{title}\t-- Acc.: {acc:.3f};\t Prec.: {prec:.3f}\t Rec.: {rec:.3f}\t F1: {f1:.3f}')
        print('Resample:', title, classifier[0], f'accuracy={acc:.3f}')
        print(metrics.classification_report(y, y_pred, labels=labels))

        plt.suptitle(f'accuracy={acc:.3f}')
        #plt.suptitle(f'good={c["good"]:,}\ninterm.={c["interm."]:,}\nbad={c["bad"]:,}', ha='left')

        sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)

        #ax.set_title(f'Accuracy = {acc:.3f}', loc='center')
        ax.set_title(
            f'good:    {c["good"]:,}\ninterm.: {c["interm."]:,}\nbad:      {c["bad"]:,}',
            fontdict={'fontsize': 9},
            loc='left'
        )

        format_axes_for_cm(ax)

        #fig.tight_layout()
        ensure_dir('./output/resampling/')
        fig.savefig(f'./output/resampling/{title}.pdf', dpi=92, bbox_inches='tight')
        plt.close(fig)

if __name__ == '__main__':
    #set_styles()
    #main()
    multiplots()
