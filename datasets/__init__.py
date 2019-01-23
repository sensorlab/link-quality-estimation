from os import path

TRACES_PATH = path.dirname(path.abspath(__file__))
PROJECT_PATH = path.dirname(TRACES_PATH)

TRANSFORM_OUTPUT_PATH = path.join(PROJECT_PATH, 'featureGenerator', 'datasets')
