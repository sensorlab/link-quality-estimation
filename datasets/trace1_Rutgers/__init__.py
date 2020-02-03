from os import path
from datasets import TRANSFORM_OUTPUT_PATH as BASE_TRANSFORM_OUTPUT_PATH

TRACE_PATH = path.dirname(path.abspath(__file__))
DATA_PATH = path.join(TRACE_PATH, 'data')

TRANSFORM_OUTPUT_PATH = path.join(
    BASE_TRANSFORM_OUTPUT_PATH,
    'dataset-1-rutgers_wifi'
)


NOISE_SOURCES = (
    # Coordinates are a mess. Rutgers declare coordinates as Node(row, column)
    # where column are x axis and rows are y axis. They also use invert y axis.

    (2, 1.5),  # between (2,1) & (2,2)
    (2, 7.5),  # between (2,7) & (2,8)
    (7, 1.5),  # between (7,1) & (7,2)
    (7, 7.5),  # between (7,7) & (7,8)
)
