from os import path
from datasets import TRANSFORM_OUTPUT_PATH as BASE_TRANSFORM_OUTPUT_PATH

TRACE_PATH = path.dirname(path.abspath(__file__))
DATA_PATH = path.join(TRACE_PATH, 'data')

TRANSFORM_OUTPUT_PATH = path.join(BASE_TRANSFORM_OUTPUT_PATH, 'dataset-2-rutgers_wifi')
