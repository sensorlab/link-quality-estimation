import itertools as it
from typing import List
import multiprocessing as mp

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn import metrics as imetrics
from imblearn import over_sampling, pipeline, under_sampling
from sklearn import ensemble, metrics, model_selection, preprocessing, tree, linear_model

from datasets.trace1_Rutgers.transform import get_traces
from tools import (PRR, CustomInterpolation, CustomMerger, SyntheticFeatures,
                    class_counter, norm_cm, poly_features, set_styles, latexify,
                    memory, format_axes_for_cm, ensure_dir)


np.random.seed(0x1234)
np.set_printoptions(precision=3)


labels = ['good', 'interm.', 'bad']


def prr_to_label(prr: float) -> str:
    if prr >= 0.9:
        return 'good'
    elif prr <= 0.1:
        return 'bad'
    else:
        return 'interm.'


feature_sets = [
    ['rssi'],
    ['rssi^2'],
    ['rssi^3'],
    ['rssi^4'],

    ['rssi^-1'],
    ['rssi^-2'],
    ['rssi^-3'],
    ['rssi^-4'],

    ['rssi_avg'],
    ['rssi_avg^2'],
    ['rssi_avg^3'],
    ['rssi_avg^4'],

    ['rssi_avg^-1'],
    ['rssi_avg^-2'],
    ['rssi_avg^-3'],
    ['rssi_avg^-4'],

    ['rssi', 'rssi_avg'],
    ['rssi', 'rssi_std'],
    ['rssi_avg', 'rssi_std'],
    ['rssi', 'rssi_avg', 'rssi_std'],

    ['rssi_avg', 'rssi_avg^2', 'rssi_avg^3', 'rssi_avg^4'],
    ['rssi_avg', 'rssi_avg^-1', 'rssi_avg^-2', 'rssi_avg^-3', 'rssi_avg^-4'],
    ['rssi_avg', 'rssi_avg^2', 'rssi_avg^3', 'rssi_avg^4', 'rssi_avg^-1', 'rssi_avg^-2', 'rssi_avg^-3', 'rssi_avg^-4'],
    ['drssi'],

    ['rssi_std'],

    # Every feature
    #[x[0] + x[1] for x in it.product(['rssi', 'rssi_avg', 'rssi_std'], ['^-4', '^-3', '^-2', '', '^-1', '^2', '^3', '^4'])]
]

@memory.cache
def load_rutgers():
    return list(get_traces())

cv = model_selection.StratifiedKFold(n_splits=10, shuffle=True)


pipe_logreg = pipeline.Pipeline([
    ('scaler', preprocessing.StandardScaler()),
    ('resample', over_sampling.RandomOverSampler()),
    ('logistic', linear_model.LogisticRegression(solver='lbfgs', max_iter=1e3, multi_class='ovr')),
])

pipe_dtree = pipeline.Pipeline([
    ('scaler', preprocessing.StandardScaler()),
    ('resample', over_sampling.RandomOverSampler()),
    ('DTree', tree.DecisionTreeClassifier()),
])


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
    dataset = dataset.drop(['noise', 'src', 'dst', 'received', 'prr'], axis=1)
    print('Drop useless features, drop lines with NaN')

    dataset = poly_features(dataset, include=['rssi', 'rssi_avg', 'rssi_std'], degree=4, include_bias=True)
    print('Polynomials applied ...')

    # Special synthetic features
    dataset['rssi^-1'] = 1. / dataset['rssi']
    dataset['rssi^-2'] = 1. / dataset['rssi^2']
    dataset['rssi^-3'] = 1. / dataset['rssi^3']
    dataset['rssi^-4'] = 1. / dataset['rssi^4']

    dataset['rssi_avg^-1'] = 1. / dataset['rssi_avg']
    dataset['rssi_avg^-2'] = 1. / dataset['rssi_avg^2']
    dataset['rssi_avg^-3'] = 1. / dataset['rssi_avg^3']
    dataset['rssi_avg^-4'] = 1. / dataset['rssi_avg^4']

    dataset['rssi_std^-1'] = 1. / dataset['rssi_std']
    dataset['rssi_std^-2'] = 1. / dataset['rssi_std^2']
    dataset['rssi_std^-3'] = 1. / dataset['rssi_std^3']
    dataset['rssi_std^-4'] = 1. / dataset['rssi_std^4']

    return dataset


@memory.cache
def different_features(pipe, features):
    dataset = prepare_data() ## cached

    dataset = dataset.replace([np.inf, -np.inf], np.nan).dropna(subset=features)

    X, y = dataset.drop(['class'], axis=1), dataset['class'].ravel()

    y_pred = model_selection.cross_val_predict(pipe, X[features].values, y, cv=cv, n_jobs=-1)

    return y, y_pred


def replacenth(original, old, new, nth):
    newString = ''

    i = 0
    count = 0
    while i < len(original):
        if original[i:i+len(old)] == old:
            count += 1
            if count > 0 and count % nth == 0:
                newString += new
                i += len(old)
                continue


        newString += original[i]
        i += 1

    return newString



# def main():
#     fig, axes = plt.subplots(6, 4, figsize=(10, 16), dpi=96, sharey=True, sharex=True)

#     for features, ax in zip(feature_sets, axes.flat):
#         y, y_pred = different_features(features)

#         acc = metrics.accuracy_score(y, y_pred)
#         cm = metrics.confusion_matrix(y, y_pred, labels=labels)
#         cm = norm_cm(cm)

#         cm = pd.DataFrame(cm, index=labels, columns=labels)
#         sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)


#         features_str = ', '.join(features)

#         features_str = replacenth(features_str, ', ', ',\n', 4)

#         features_str = features_str \
#             .replace('_std', '$_{\\mathrm{std}}$') \
#             .replace('_avg', '$_{\\mathrm{avg}}$') \
#             .replace('^-1', '$^{-1}$') \
#             .replace('^-2', '$^{-2}$') \
#             .replace('^-3', '$^{-3}$') \
#             .replace('^-4', '$^{-4}$') \
#             .replace('^2', '$^{2}$') \
#             .replace('^3', '$^{3}$') \
#             .replace('^4', '$^{4}$')


#         ax.set_title(f'{features_str}\naccuracy={acc:.3f}')


#     fig.tight_layout()
#     fig.savefig('./different_features.pdf', bbox_inches='tight')

#     plt.show()


def stringify_features(features: List[str]) -> str:
    return '__' \
        .join(features) \
        .replace('^', '_') \
        .replace('*', '_')



def multiple_figures():
    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])

    latexify()

    pipe = pipe_dtree

    for features in feature_sets:
        y, y_pred = different_features(pipe, features)

        print(features, 'DTree')
        print(metrics.classification_report(y, y_pred, labels=labels))

        #prec = metrics.precision_score(y, y_pred, labels=labels, average='micro')
        #rec = metrics.recall_score(y, y_pred, labels=labels, average='micro')

        if 0:

            acc = metrics.accuracy_score(y, y_pred)
            prec = metrics.precision_score(y, y_pred, average='weighted', labels=labels)
            recall = metrics.recall_score(y, y_pred, average='weighted', labels=labels)


            cm = metrics.confusion_matrix(y, y_pred, labels=labels)
            cm = norm_cm(cm)

            cm = pd.DataFrame(cm, index=labels, columns=labels)

            fig, ax = plt.subplots(dpi=92)
            sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
            format_axes_for_cm(ax)

            feature_str = stringify_features(features)
            ax.set_title(f'Accuracy = {acc:.3f}\n(prec = {prec:.3f}; rec = {recall:.3f})')

            fig.tight_layout()

            ensure_dir('./output/features/dtree/')
            fig.savefig(f'./output/features/dtree/{feature_str}.pdf', dpi=92, bbox_inches='tight')
            plt.close(fig)
            print(f'Done {features}')



    pipe = pipe_logreg

    for features in feature_sets:
        y, y_pred = different_features(pipe, features)

        print(features, 'Logistic')
        print(metrics.classification_report(y, y_pred, labels=labels))

        if 0:
            acc = metrics.accuracy_score(y, y_pred)
            prec = metrics.precision_score(y, y_pred, average='micro', labels=labels)
            recall = metrics.recall_score(y, y_pred, average='micro', labels=labels)

            #prec = metrics.precision_score(y, y_pred, labels=labels, average='micro')
            #rec = metrics.recall_score(y, y_pred, labels=labels, average='micro')

            cm = metrics.confusion_matrix(y, y_pred, labels=labels)
            cm = norm_cm(cm)

            cm = pd.DataFrame(cm, index=labels, columns=labels)

            fig, ax = plt.subplots(dpi=92)
            sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
            format_axes_for_cm(ax)

            feature_str = stringify_features(features)
            ax.set_title(f'Accuracy = {acc:.3f}\n(prec = {prec:.3f}, rec = {recall:.3f})')

            fig.tight_layout()

            ensure_dir('./output/features/logistic/')
            fig.savefig(f'./output/features/logistic/{feature_str}.pdf', dpi=92, bbox_inches='tight')
            plt.close(fig)
            print(f'Done {features}')


if __name__ == '__main__':
    #set_styles()
    multiple_figures()
    #main()
