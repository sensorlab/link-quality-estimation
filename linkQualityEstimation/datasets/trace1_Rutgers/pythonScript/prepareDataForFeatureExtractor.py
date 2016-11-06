import os
import sys
import pandas as pd
from shutil import rmtree

PATH = "../data/"
FEATURE_EXTRACTOR_DATASETS = "../../../featureGenerator/datasets/dataset-2-rutgers_wifi/"
NUMBER_OF_PACKETS = 300.0
RSSI_MAX = 127
RSSI_MIN = 0
NUMBER_OF_BINS = 40
MISSING_DATA_BIN = -1
WINDOW_SIZE = 30

print "Start per link transformation"
PRR = []
RSSI_MEAN = []
PRR_WINDOW = []
RSSI_WINDOW = []
numberOfExperiments = 0
tmpDir = ""
# Create dataset directory
if os.path.exists(FEATURE_EXTRACTOR_DATASETS):
    rmtree(FEATURE_EXTRACTOR_DATASETS)
os.makedirs(FEATURE_EXTRACTOR_DATASETS)
for root, dirs, files in os.walk(PATH):
    root = root.lstrip()
    print root
    tmp = root[len(PATH):]
    dir = tmp.split("/")
    for file in files:
        if file.endswith(""):
            x, y = [], []
            missing_values = 0
            fiveNumSummary = 0
            name = dir[1].split("_")
            fromNode = name[1]
            toNode = str("node" + file[len("sdec"):])
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    if int(data[0]) < NUMBER_OF_PACKETS and int(data[1]) <= RSSI_MAX and int(data[1]) >= RSSI_MIN:
                        x.append(data[0])
                        y.append(int(data[1]))
            file.close()
            missing_values = (NUMBER_OF_PACKETS - len(y))

            if len(y) > 0:
                # Create directory path if it is missing
                if tmpDir != dir[0]:
                    numberOfExperiments += 1

                experimentPath = FEATURE_EXTRACTOR_DATASETS + "experiment-" + str(numberOfExperiments) + "-noise_level_" + dir[0]
                if not os.path.exists(experimentPath):
                    tmpDir = dir[0]
                    os.makedirs(experimentPath)


                # Create csv file per link
                csvFile = experimentPath + "/trans-" + fromNode + "-recev-" + toNode + ".csv"
                print "trans-" + fromNode + "-recev-" + toNode + ".csv"
                df = pd.DataFrame({"seq": x, "rssi": y})
                # Keep colum order
                df = df[['seq', 'rssi']]
                df.to_csv(csvFile, index=False, header=True, cols=['seq', 'rssi'])
