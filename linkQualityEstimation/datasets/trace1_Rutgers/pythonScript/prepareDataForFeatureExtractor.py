import os
import sys
import pandas as pd
from shutil import rmtree
from natsort import natsorted
import numpy as np
import sys

PATH = "../data/"
FEATURE_EXTRACTOR_DATASETS = "../../../featureGenerator/datasets/dataset-2-rutgers_wifi/"
NUMBER_OF_PACKETS = 300
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
for root, dirs, files in natsorted(os.walk(PATH)):
    root = root.lstrip()
    print root
    tmp = root[len(PATH):]
    dir = tmp.split("/")
    for file in files:
        if file.endswith(""):
            x, y, z = [], [], []
            current_seq = 0
            previous_rssi = RSSI_MIN
            previous_seq = -1
            missing_values = 0
            fiveNumSummary = 0
            name = dir[1].split("_")
            fromNode = name[1].replace("-", "_")
            toNode = str("node" + file[len("sdec"):]).replace("-", "_")
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    rssi = int(data[1])
                    seq = int(data[0])
                    if seq < NUMBER_OF_PACKETS and rssi <= RSSI_MAX and rssi >= RSSI_MIN:
                        avg_rssi = np.mean((previous_rssi, rssi))
                        std_rssi = np.std((previous_rssi, rssi))
                        std_rssi = std_rssi if std_rssi > 0 else sys.float_info.min
                        difference = seq - previous_seq - 1
                        x.extend(range(previous_seq + 1, int(data[0])))
                        y.extend(np.random.normal(avg_rssi, std_rssi, size=difference))
                        z.extend(["false"] * difference)
                        
                        x.append(seq)
                        y.append(rssi)
                        z.append("true")
                        previous_seq = seq
                        previous_rssi = rssi
            difference = NUMBER_OF_PACKETS - previous_seq - 1
            avg_rssi = np.mean((previous_rssi, RSSI_MIN))
            std_rssi = np.std((previous_rssi, RSSI_MIN))
            std_rssi = std_rssi if std_rssi > 0 else sys.float_info.min
            x.extend(range(previous_seq + 1, NUMBER_OF_PACKETS))
            y.extend(np.random.normal(avg_rssi, std_rssi, size=difference))
            z.extend(["false"] * difference)

            file.close()
            #missing_values = (NUMBER_OF_PACKETS - len(y))

            if len(y) > 0:
                # Create directory path if it is missing
                if tmpDir != dir[0]:
                    numberOfExperiments += 1

                experimentPath = FEATURE_EXTRACTOR_DATASETS + "experiment-" + str(numberOfExperiments) + "-noise_level_" + dir[0].replace("-", "_")
                if not os.path.exists(experimentPath):
                    tmpDir = dir[0]
                    os.makedirs(experimentPath)


                # Create csv file per link
                csvFile = experimentPath + "/trans-" + fromNode + "-recv-" + toNode + ".csv"
                print "trans-" + fromNode + "-recv-" + toNode + ".csv"
                df = pd.DataFrame({"seq": x, "rssi": y, "received": z})
                # Keep colum order
                df = df[['seq', 'rssi', 'received']]
                df.to_csv(csvFile, index=False, header=True, cols=['seq', 'rssi', 'received'])
