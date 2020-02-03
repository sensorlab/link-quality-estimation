import itertools as it
import numpy as np
import matplotlib as mpl

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

np.random.seed(0x1234)
np.set_printoptions(precision=3)

from sklearn import ensemble, tree, model_selection, preprocessing, metrics, dummy, ensemble, linear_model, neighbors, neural_network, svm
from imblearn import over_sampling, under_sampling, pipeline, metrics as imetrics

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
    latexify,
    format_axes_for_cm,
    memory,
    ensure_dir
)

labels = ['good', 'interm.', 'bad']

features = ['rssi', 'rssi_avg', 'rssi_std']

@memory.cache
def load_rutgers():
    return list(get_traces())


cv = model_selection.StratifiedKFold(n_splits=10, shuffle=True)

def prr_to_label(prr: float) -> str:
    if prr >= 0.9:
        return 'good'
    elif prr <= 0.1:
        return 'bad'
    else:
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


    dataset = dataset.dropna()
    dataset = dataset.drop(['noise', 'src', 'dst', 'received', 'prr'], axis=1)
    print('Drop useless features, drop lines with NaN')

    return dataset


@memory.cache
def different_models(pipe):

    dataset = prepare_data()

    X, y = dataset[features].values, dataset['class'].ravel()

    y_pred = model_selection.cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    return y, y_pred



def multiple_figures():
    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])
    latexify()


    cv = model_selection.StratifiedKFold(n_splits=10, shuffle=True)
    scaler = preprocessing.StandardScaler()
    resample = over_sampling.RandomOverSampler()

    baseline = pipeline.make_pipeline(
        scaler,
        resample,
        dummy.DummyClassifier(strategy='constant', constant='good')
    )

    logreg = pipeline.make_pipeline(
        scaler,
        resample,
        linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr'),
    )

    dtree = pipeline.make_pipeline(
        scaler,
        resample,
        tree.DecisionTreeClassifier(),
    )

    knn = pipeline.make_pipeline(
        scaler,
        resample,
        neighbors.KNeighborsClassifier(),
    )

    mlp = pipeline.make_pipeline(
        scaler,
        resample,
        neural_network.MLPClassifier(
            hidden_layer_sizes=(100,100,100,),
            activation='relu',
            solver='adam'
        ),
    )

    svc = pipeline.make_pipeline(
        scaler,
        resample,
        svm.LinearSVC(),
    )

    RForest = pipeline.make_pipeline(
        scaler,
        resample,
        ensemble.RandomForestClassifier(n_estimators=100),
    )

    models = (
        ('Constant', baseline),
        ('Logistic Regression', logreg),
        ('Decision Tree', dtree),
        #('kNN', knn),
        ('Multi-Layer Perceptron', mlp),
        ('linearSVM', svc),
        ('Random Forest', RForest),
    )


    # Special case of baseline
    filename = 'baseline-link-overall'
    df = prepare_data()
    y, y_pred = df['class'].ravel(), df['class_overall'].ravel()

    acc = metrics.accuracy_score(y, y_pred)
    prec = metrics.precision_score(y, y_pred, average='weighted', labels=labels)
    recall = metrics.recall_score(y, y_pred, average='weighted', labels=labels)

    cm = metrics.confusion_matrix(y, y_pred, labels=labels)
    cm = norm_cm(cm)

    cm = pd.DataFrame(cm, index=labels, columns=labels)

    fig, ax = plt.subplots(dpi=92)
    sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
    ax.set_title(f'accuracy = {acc:.3f}\n(prec = {prec:.3f}, rec = {recall:.3f})')
    format_axes_for_cm(ax)

    fig.tight_layout()

    ensure_dir('./output/models/')
    fig.savefig(f'./output/models/{filename}.pdf', dpi=92, bbox_inches='tight')
    plt.close(fig)
    print(f'Done {filename}')





    for name, pipe in models:
        filename = name.lower().replace(' ', '_')

        y, y_pred = different_models(pipe)

        acc = metrics.accuracy_score(y, y_pred)
        #prec = metrics.precision_score(y, y_pred, average='weighted', labels=labels)
        #recall = metrics.recall_score(y, y_pred, average='weighted', labels=labels)
        print(name)
        print(metrics.classification_report(y, y_pred, labels=labels))

        cm = metrics.confusion_matrix(y, y_pred, labels=labels)
        cm = norm_cm(cm)

        cm = pd.DataFrame(cm, index=labels, columns=labels)

        fig, ax = plt.subplots(dpi=92)
        sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)
        ax.set_title(f'accuracy={acc:.3f}')
        format_axes_for_cm(ax)

        fig.tight_layout()

        ensure_dir('./output/models/')
        fig.savefig(f'./output/models/{filename}.pdf', dpi=92, bbox_inches='tight')
        plt.close(fig)



def main():
    cv = model_selection.StratifiedKFold(n_splits=10, shuffle=True)
    poly = preprocessing.PolynomialFeatures(degree=2)
    scaler = preprocessing.StandardScaler()
    resample = over_sampling.RandomOverSampler()

    baseline = pipeline.make_pipeline(
        scaler,
        resample,
        dummy.DummyClassifier(strategy='constant', constant='good')
    )

    logreg = pipeline.make_pipeline(
        scaler,
        resample,
        linear_model.LogisticRegression(),
    )

    dtree = pipeline.make_pipeline(
        scaler,
        resample,
        tree.DecisionTreeClassifier(),
    )

    #knn = pipeline.make_pipeline(
    #    scaler,
    #    resample,
    #    neighbors.KNeighborsClassifier()
    #)

    mlp = pipeline.make_pipeline(
        scaler,
        resample,
        neural_network.MLPClassifier()
    )

    svc = pipeline.make_pipeline(
        scaler,
        resample,
        svm.LinearSVC()
    )

    RForest = pipeline.make_pipeline(
        scaler,
        resample,
        ensemble.RandomForestClassifier()
    )

    models = (
        ('Constant', baseline),
        ('Logistic Regression', logreg),
        ('Decision Tree', dtree),
        #('kNN', knn),
        ('Multi-Layer Perceptron', mlp),
        ('SVM (linear kernel)', svc),
        ('Random Forest', RForest),
    )



    fig, axes = plt.subplots(nrows=2, ncols=3, dpi=96, sharey=True, sharex=True)

    for (name, pipe), ax in zip(models, axes.reshape(-1)):
        y, y_pred = different_models(pipe)

        acc = metrics.accuracy_score(y, y_pred)
        prec = metrics.precision_score(y, y_pred, average='weighted', labels=labels)
        recall = metrics.recall_score(y, y_pred, average='weighted', labels=labels)


        cm = metrics.confusion_matrix(y, y_pred, labels=labels)
        cm = norm_cm(cm)

        cm = pd.DataFrame(cm, index=labels, columns=labels)
        sns.heatmap(cm, vmin=0, vmax=1, annot=True, fmt='.2f', cmap='Greys', ax=ax, cbar=False, square=True)

        ax.set_title(f'{name}\naccuracy={acc:.3f}\n(prec = {prec:.3f}, rec = {recall:.3f})')


    fig.tight_layout()
    fig.savefig('./different_models.pdf', bbox_inches='tight')

    plt.show()


if __name__ == '__main__':
    #set_styles()
    #main()

    multiple_figures()
