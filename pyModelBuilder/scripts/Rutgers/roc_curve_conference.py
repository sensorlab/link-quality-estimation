import itertools as it
import numpy as np
import matplotlib as mpl

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

SEED = 0xABCD
np.random.seed(SEED)
np.set_printoptions(precision=3)

from sklearn import ensemble, tree, model_selection, preprocessing, metrics, dummy, ensemble, linear_model, neighbors, neural_network, svm, pipeline
from imblearn import over_sampling, under_sampling, pipeline as ipipeline, metrics as imetrics

from datasets.trace1_Rutgers.transform import get_traces
from tools import (
    CustomInterpolation,
    SyntheticFeatures,
    CustomMerger,
    PRR,
    class_counter,
    norm_cm,
    set_styles,
    poly_features,
    memory,
)


# Helpers
def latexify(fig_width=None, fig_height=None, columns=1, scale=1.0):
    from math import sqrt
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}, how many columns it covers
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert(columns in [1,2])
    
    #width  = 3.487
    #height = width / 1.618

    if fig_width is None:
        fig_width = 3.39 if columns==1 else 6.9 # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5) - 1.0) / 2.0    # Aesthetic ratio
        fig_height = fig_width * golden_mean # height in inches
        
        
    fig_height *= scale
    fig_width *= scale

    MAX_HEIGHT_INCHES = 16.0 * scale
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height + 
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {
        # Use LaTex to write all text
        'text.usetex': True,
        'font.family': 'serif',
        #'font.serif': 'Times',
        # Use 10pt font in plots, to match 10pt font in document
        'axes.labelsize': 6,
        'font.size': 6,
        # Make the legend/label fonts a little smaller
        'legend.fontsize': 6,
        'xtick.labelsize': 6,
        'ytick.labelsize': 6,
        
        'figure.autolayout': True,
        'figure.figsize': [fig_width, fig_height],
        
        'savefig.format': 'pdf',
        'savefig.bbox': 'tight',
        
        'pdf.fonttype': 42,
        
        #'legend.framealpha': 0.2,
        
        'grid.color': '0.9',
        'grid.linestyle': ':',
    }
    
    mpl.style.use('default')
    mpl.style.use(['seaborn-notebook', 'seaborn-whitegrid', 'seaborn-ticks'])
    mpl.rcParams.update(params)
    

def set_size(width, fraction=1):
    from math import sqrt
    # SRC: https://jwalton.info/Embed-Publication-Matplotlib-Latex/
    
    # 252.0pt is IEEEtrans columnwidth (\showthe\columnwidth)
    
    
    if width == 'thesis':
        width_pt = 426.79135
    elif width == 'beamer':
        width_pt = 307.28987
    elif width == 'pnas':
        width_pt = 246.09686
    else:
        width_pt = width
    
    fig_width_pt = width_pt * fraction
    inches_per_pt = 1.0 / 72.27
    golden_ratio = (5**.5 - 1) / 2.0
    
    fig_width_in = fig_width_pt * inches_per_pt
    fig_height_in = fig_width_in * golden_ratio
    fig_dim = (fig_width_in, fig_height_in)
    return fig_dim


def format_axes(ax, SPINE_COLOR='gray', despine=False):
    
    if despine:
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        

    for spine in ['left', 'bottom', 'top', 'right']:
        ax.spines[spine].set_color(SPINE_COLOR)
        ax.spines[spine].set_linewidth(0.5)

    #ax.xaxis.set_ticks_position('bottom')
    #ax.yaxis.set_ticks_position('left')

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction='out', color=SPINE_COLOR)

    return ax


def ensure_dir(path: str):
    from pathlib import Path
    _path = Path(path)
    _path.parent.mkdir(parents=True, exist_ok=True)
    return path


latexify(columns=2)



labels = ['good', 'interm.', 'bad']

features = ['rssi', 'rssi_avg', 'rssi_std']

@memory.cache
def load_rutgers():
    return list(get_traces())

def prr_to_label(prr: float) -> str:
    if prr >= 0.9:
        return 'good'

    if prr <= 0.1:
        return 'bad'

    return 'interm.'


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

    for df in dataset:
        df['class_overall'] = prr_to_label( df['received'].astype(bool).sum() / 300. )
    print('Created special feature `class_overall`')

    dataset = CustomMerger().fit_transform(dataset)
    print('Datasets merged ...')

    dataset['class'] = dataset['prr'].apply(prr_to_label)
    print('Classification applied ...')


    #dataset = dataset.dropna()
    dataset = dataset.sample(frac=1, random_state=SEED)

    return dataset

@memory.cache
def get_classification(pipe):
    dataset = prepare_data()

    dataset = dataset[[*features, 'class']].dropna()

    X, y = dataset[features].values, dataset['class'].ravel()

    y_pred = model_selection.cross_val_predict(
        estimator=pipe,
        X=X,
        y=y,
        cv=model_selection.StratifiedKFold(n_splits=10, shuffle=True, random_state=SEED),
        n_jobs=-1
    )

    return y, y_pred


def curves():
    from sklearn import multiclass
    from itertools import cycle

    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])
    latexify()

    baseline = ipipeline.make_pipeline(
        over_sampling.RandomOverSampler(random_state=SEED),
        dummy.DummyClassifier(strategy='constant', constant=1, random_state=SEED),
    )

    logreg = ipipeline.make_pipeline(
        over_sampling.RandomOverSampler(random_state=SEED),
        linear_model.LogisticRegression(solver='lbfgs', random_state=SEED),
    )

    dtree = ipipeline.make_pipeline(
        over_sampling.RandomOverSampler(random_state=SEED),
        tree.DecisionTreeClassifier(max_depth=3, random_state=SEED),
    )


    models = (
        ('Constant', baseline),
        ('Logistic Regression', logreg),
        ('Decision Tree', dtree),
    )

    for name, pipe in models:
        classifier = multiclass.OneVsRestClassifier(pipe)

        df = prepare_data()
        df = df[[*features, 'class']].dropna()

        X, y = df[features].values, df['class'].ravel()
        y = preprocessing.label_binarize(y, classes=labels)

        n_labels = 3
        #n_samples, n_features = X.shape


        X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=.2, random_state=SEED)

        classifier.fit(X_train, y_train)


        if hasattr(classifier, 'decision_function'):
            y_score = classifier.decision_function(X_test)
        
        if hasattr(classifier, 'predict_proba'):
            y_score = classifier.predict_proba(X_test)

        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(n_labels):
            fpr[i], tpr[i], _ = metrics.roc_curve(y_test[:, i], y_score[:, i])
            roc_auc[i] = metrics.auc(fpr[i], tpr[i])

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = metrics.roc_curve(y_test.ravel(), y_score.ravel())
        roc_auc["micro"] = metrics.auc(fpr["micro"], tpr["micro"])


        # First aggregate all false positive rates
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_labels)]))

        # Then interpolate all ROC curves at this points
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(n_labels):
            mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])


        # Finally average it and compute AUC
        mean_tpr /= n_labels

        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = metrics.auc(fpr["macro"], tpr["macro"])

        # Plot all ROC curves
        latexify(columns=1)
        f, ax = plt.subplots()


        ax.plot(
            fpr["micro"],
            tpr["micro"],
            label=f'micro-average ROC curve (area = {roc_auc["micro"]:0.2f})',
            color='deeppink',
            linestyle=':'
        )

        ax.plot(
            fpr["macro"],
            tpr["macro"],
            label=f'macro-average ROC curve (area = {roc_auc["macro"]:0.2f})',
            color='navy',
            linestyle=':'
        )

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        for i, color in zip(range(n_labels), colors):
            ax.plot(
                fpr[i], 
                tpr[i], 
                color=color,
                label=f'ROC curve of class {labels[i]} (area = {roc_auc[i]:0.2f})'
            )



        ax.plot([0, 1], [0, 1], 'k--')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('FP Rate')
        ax.set_ylabel('TP Rate')
        #ax.set_title(f'Multi-class ROC curves for {name}')
        ax.legend(loc="lower right")
        format_axes(ax)
        #f.tight_layout()
        f.savefig(f'./output/roc-{name.replace(" ", "-").lower()}.pdf', bbox_inches='tight')

if __name__ == '__main__':
    curves()