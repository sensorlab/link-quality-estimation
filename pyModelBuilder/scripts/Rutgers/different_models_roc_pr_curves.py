import itertools as it
import numpy as np
import matplotlib as mpl

import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

np.random.seed(0x1234)
np.set_printoptions(precision=3)

random_state = np.random.RandomState(0x1234)

from sklearn import ensemble, tree, model_selection, preprocessing, metrics, dummy, ensemble, linear_model, neighbors, neural_network, svm, multiclass, kernel_approximation
from imblearn import over_sampling, under_sampling, pipeline, metrics as imetrics

from datasets import load_rutgers
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
    format_axes_for_chart,
    latexify, ensure_dir
)


classes = ['good', 'interm.', 'bad']
n_classes = len(classes)

features = ['rssi', 'rssi_avg', 'rssi_std']


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

    dataset = SyntheticFeatures(source='rssi', window_size=20).fit_transform(dataset)
    print('Synthetic features created ...')

    dataset = PRR(source='received', window_size=20, ahead=1, target='prr').fit_transform(dataset)
    print('PRR created ...')

    dataset = CustomMerger().fit_transform(dataset)
    print('Datasets merged ...')

    dataset['class'] = dataset['prr'].apply(prr_to_label)
    print('Classification applied ...')


    dataset = dataset.dropna()
    dataset = dataset.drop(['noise', 'src', 'dst', 'received', 'prr'], axis=1)
    print('Drop useless features, drop lines with NaN')

    return dataset



def main():
    mpl.style.use(['seaborn-white', 'seaborn-paper', 'grayscale'])
    latexify(columns=2)

    #cv = model_selection.StratifiedKFold(n_splits=10, shuffle=True)
    #poly = preprocessing.PolynomialFeatures(degree=2)
    scaler = preprocessing.StandardScaler()
    resample = over_sampling.RandomOverSampler()

    baseline = pipeline.make_pipeline(
        scaler,
        resample,
        dummy.DummyClassifier(strategy='constant', constant=0)
    )
    
    logreg = pipeline.make_pipeline(
        scaler,
        resample,
        linear_model.LogisticRegression(),
    )

    sgd = pipeline.make_pipeline(
        scaler,
        resample,
        linear_model.SGDClassifier(),
    )

    dtree = pipeline.make_pipeline(
        scaler,
        resample,
        tree.DecisionTreeClassifier(),
    )

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
        ('Logistic Reg.', logreg),
        ('Decision Tree', dtree),
        #('kNN', knn),
        ('Multi-Layer Perceptron', mlp),
        ('SVM (linear kernel)', svc),
        ('Random Forest', RForest),
    )


    colors = sns.color_palette("cubehelix", len(models))


    fig, ax = plt.subplots(dpi=92) # Setup a figure

    #ax.set_title('Precision-Recall curve')

    #ax.set_xlim(0, 1)
    #ax.set_ylim(0, 1)

    ax.set_xlabel('Recall = $\\frac{{TP}}{{TP+FN}}$')
    ax.set_ylabel('Precision = $\\frac{{TP}}{{TP+FP}}$')


    # Prepare data for processing
    data = prepare_data()
    X, y = data[['rssi', 'rssi_avg', 'rssi_std']].values, data['class'].ravel()
    Y = preprocessing.label_binarize(y, classes=classes)
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, Y, test_size=0.2, random_state=random_state)

    for (name, model), color in zip(models, colors):
        classifier = multiclass.OneVsRestClassifier(model) # Make model support *.decision_function

        classifier.fit(X_train, y_train)

        # generate y_score
        if hasattr(classifier, 'decision_function'):
            y_score = classifier.decision_function(X_test)
        else:
            y_score = classifier.predict_proba(X_test)
            #continue

        # generate probabilities
        #y_proba = classifier.predict_proba(X_test)

        # generate predictions
        y_pred = classifier.predict(X_test)

        precision = dict()
        recall = dict()
        average_precision = dict()

        acc = metrics.accuracy_score(y_test, y_pred)

        for i in [1]: # We observe only intermediate class
            precision[i], recall[i], _ = metrics.precision_recall_curve(y_test[:, i], y_score[:, i])
            average_precision[i] = metrics.average_precision_score(y_test[:, i], y_score[:, i])

            ax.step(recall[i], precision[i], where='post', color=color, alpha=0.65, label=f'{name}')

        print(f'Plotted {name}')


    ax.legend(loc="best")
    format_axes_for_chart(ax)
    fig.tight_layout()

    ensure_dir('./output/')
    fig.savefig('./output/precision-recall-curve.pdf', dpi=92, bbox_inches='tight')
    #plt.show()
    plt.close(fig)




if __name__ == '__main__':
    main()