from os import path

from setuptools import setup


def read(fname):
    with open(path.join(path.dirname(__file__), fname)) as f:
        return f.read()

requirements = [
    'numpy',
    'scipy',
    'pandas',
    'matplotlib',
    'seaborn',
]

setup(
    name='LQE',
    version='0.1',
    url='https://github.com/sensorlab/link-quality-estimation',
    author='SensorLab',
    author_email='sensorlab@ijs.si',
    description='Collection of link quality estimation (LQE) trace-sets for reasearchers',
    long_description=read('README.md'),
    license='GPL3+',
    packages=['datasets'],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[],
    extras_require={
        'extra': requirements,
        'dev': ['pylint', 'autopep8'],
        'ml': ['scikit-learn<0.20', 'imbalanced-learn', 'sklearn-pandas', 'scikit-image', 'joblib'],
        'lab': ['jupyterlab', 'joblib'],
        'cluster': ['ipyparallel'],
    },
)
