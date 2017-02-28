from shutil import rmtree
import pandas as pd
import os

PATH_TO_DATA_FILE = "../data/css/Y.css"
FEATURE_EXTRACTOR_DATASETS = "../../../featureGenerator/datasets/dataset-4-michigan_CC1000/"

NUMBER_SENSORS = 14

# Create dataset directory
if os.path.exists(FEATURE_EXTRACTOR_DATASETS):
    rmtree(FEATURE_EXTRACTOR_DATASETS)
os.makedirs(FEATURE_EXTRACTOR_DATASETS)

link_number = 0
file = open(PATH_TO_DATA_FILE, 'r')
for line in file:
    # Node numbering
    node1 = link_number // NUMBER_SENSORS + 1
    node2 = link_number % NUMBER_SENSORS + 1
    if node1 == node2:
        node2 += 1
        link_number += 2
    else:
        link_number += 1

    y = []
    # ignore_leading = True
    for measurement in line.split(","):
        # Measurements are asynchronous, ignore leading zeros
        # if ignore_leading:
        #    if float(measurement) == 0:
        #        continue
        #    ignore_leading = False
        y.append(float(measurement))

    experimentPath = FEATURE_EXTRACTOR_DATASETS + "experiment-1-unidirectional_links"

    if not os.path.exists(experimentPath):
        os.makedirs(experimentPath)

    # Create csv file per link
    # id = node that is transmitting the data
    # mnt = monitor that is receiving the data
    csvFile = experimentPath + "/trans-" + str(node1) + "-recv-" + str(node2) + ".csv"
    df = pd.DataFrame({"rssi": y})
    # Keep colum order
    df = df[['rssi']]
    df.to_csv(csvFile, index=False, header=True, cols=['seq', 'rssi'])


file.close()
