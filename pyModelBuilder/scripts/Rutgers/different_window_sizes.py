import itertools as it
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn import metrics as imetrics
from imblearn import over_sampling, pipeline, under_sampling
from sklearn import ensemble, metrics, model_selection, preprocessing, tree, linear_model
from sklearn.externals.joblib import Memory

from datasets.trace1_Rutgers.transform import get_traces
from tools import (PRR, CustomInterpolation, CustomMerger, SyntheticFeatures,
                     class_counter, norm_cm, memory, latexify, format_axes_for_chart,
                     format_axes_for_cm, ensure_dir)

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

@memory.cache
def load_rutgers():
    return list(get_traces())


features = ['rssi', 'rssi_std', 'rssi_avg']

cv = model_selection.StratifiedKFold(n_splits=10, shuffle=True)

pipe = pipeline.Pipeline([
    ('scaler', preprocessing.StandardScaler()),
    ('resample', over_sampling.RandomOverSampler()),
    #('clf', tree.DecisionTreeClassifier(max_depth=3)),
    ('linear', linear_model.LogisticRegression(solver='ovr')),
])


@memory.cache
def different_window_sizes(W_PRR, W_HISTORY):
    print(f'*** PRR={W_PRR}, HISTORY={W_HISTORY} ***')

    dataset = load_rutgers()
    print('Rutgers loaded ...')

    dataset = CustomInterpolation(source='rssi', strategy='constant', constant=0).fit_transform(dataset)
    print('Interpolation applied ...')

    dataset = SyntheticFeatures(source='rssi', window_size=W_HISTORY).fit_transform(dataset)
    print('Synthetic features created ...')

    dataset = PRR(source='received', window_size=W_PRR, ahead=1, target='prr').fit_transform(dataset)
    print('PRR created ...')

    dataset = CustomMerger().fit_transform(dataset)
    print('Datasets merged ...')

    dataset['class'] = dataset['prr'].apply(prr_to_label)
    print('Classification applied ...')

    dataset = dataset.dropna()

    X, y = dataset[features].copy(), dataset['class'].ravel()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    return y, y_pred


def main():
    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])
    latexify()

    w_sizes = (5, 10, 50, 100)



    for (w_prr, w_history) in it.product(w_sizes, repeat=2):
        y, y_pred = different_window_sizes(w_prr, w_history)

        acc = metrics.accuracy_score(y, y_pred)
        prec = metrics.precision_score(y, y_pred, average='weighted', labels=labels)
        recall = metrics.recall_score(y, y_pred, average='weighted', labels=labels)
        f1 = metrics.f1_score(y, y_pred, average='weighted', labels=labels)

        print(f'& {w_history}\t& {w_prr}\t& {acc:.3f}\t& {prec:.3f}\t& {recall:.3f}\t& {f1:.3f}')


        #print(f'Wh=={w_history}; Wprr=={w_prr}')
        #print(metrics.classification_report(y, y_pred, labels=labels))

        cm = metrics.confusion_matrix(y, y_pred, labels=labels)
        cm = norm_cm(cm)
        cm = pd.DataFrame(cm, index=labels, columns=labels)


        fig, ax = plt.subplots(dpi=92)
        sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
        #ax.set_title(f'$\\mathrm{{Acc}}(W_{{\\mathrm{{PRR}}}}={w_prr}, W_{{\\mathrm{{history}}}}={w_history})={acc:.3f}$')
        ax.set_title(f'Accuracy = {acc:.3f}\n(prec = {prec:.3f}, rec = {recall:.3f})')
        format_axes_for_cm(ax)

        fig.tight_layout()

        ensure_dir('./output/w_sizes/')
        fig.savefig(f'./output/w_sizes/Wprr{w_prr}_Wh{w_history}.pdf', dpi=92, bbox_inches='tight')
        plt.close(fig)




def advanced_charts():
    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])
    latexify(columns=2)

    w_sizes = (2, 5, 10, 15, 20, 30, 50, 80, 100)[::-1] # [::-1] will reverse order

    fig, ax = plt.subplots(dpi=92)

    colors = sns.color_palette("cubehelix", len(w_sizes))

    for w_prr, color in zip(w_sizes, colors):
        acc = []
        for w_history in w_sizes:
            y, y_pred = different_window_sizes(w_prr, w_history)
            acc.append(metrics.accuracy_score(y, y_pred))

        ax.plot(w_sizes, acc, label=f'W$_\\mathrm{{PRR}}={w_prr}$', color=color)


    ax.set_ylabel('accuracy')
    ax.set_xlabel(f'W$_\\mathrm{{history}}$')
    ax.set_xticks(w_sizes[::-1])
    ax.set_xlim(min(w_sizes), max(w_sizes))
    format_axes_for_chart(ax)

    fig.tight_layout()
    fig.legend(loc='right')

    ensure_dir('./output/')
    fig.savefig('./output/different_window_sizes_linechart.pdf', dpi=92, bbox_inches='tight')

    plt.close(fig)
    #plt.show()



if __name__ == '__main__':
    main()
    #advanced_charts()
