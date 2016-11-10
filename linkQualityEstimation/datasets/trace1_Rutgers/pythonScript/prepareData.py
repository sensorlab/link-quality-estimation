import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
import matplotlib.mlab as mlab
import pandas as pd
PATH = "../data/"
PATH_TO_FIGURE = "../figures/perLink/"
PATH_TO_NEW_DATASET = "../histogramClustering/"
NUMBER_OF_PACKETS = 300.0
NUMBER_OF_BINS = 40
RSSI_MAX = 127
RSSI_MIN = 0
MISSING_DATA_BIN = -1


def createFiles():
    fileList = ["dbm0.arff", "dbm-5.arff", "dbm-10.arff", "dbm-15.arff", "dbm-20.arff"]
    for file in fileList:
        file = open(PATH_TO_NEW_DATASET + file, 'w')
        file.write("@RELATION transmitted\n")
        file.write("@ATTRIBUTE from     string\n")
        file.write("@ATTRIBUTE to     string\n")
        file.write("@ATTRIBUTE linkName     string\n")
        file.write("@ATTRIBUTE PDR     numeric\n")
        file.write("@ATTRIBUTE RSSI_MEAN     numeric\n")
        for bin in range(MISSING_DATA_BIN, NUMBER_OF_BINS):
            file.write("@ATTRIBUTE bin_%s     numeric\n" % (bin))

        file.write("@DATA\n")
        file.close()
count = 0
createFiles()
for root, dirs, files in os.walk(PATH):
    x, y = [], []
    missing_values = 0
    fiveNumSummary = 0
    root = root.lstrip()
    tmp = root[len(PATH):]
    dir = tmp.split("/")
    histogramData = open(PATH_TO_NEW_DATASET + dir[0] + '.arff', 'a')
    print "Transmittion power:", dir[0]
    for file in files:
        tmp_x, tmp_y = [], []
        if file.endswith(""):
            name = dir[1].split("_")
            fromNode = name[1]
            toNode = str("node" + file[len("sdec"):])
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    if int(data[1]) > RSSI_MAX:
                        count = count + 1
                    if int(data[1]) <= RSSI_MAX and int(data[1]) >= RSSI_MIN:
                        tmp_x.append(data[0])
                        tmp_y.append(int(data[1]))

            histogramData.write("%s, %s, %s" % (fromNode, toNode, (fromNode + "TO" + toNode)))
            if len(tmp_y) <=NUMBER_OF_PACKETS:
                histogramData.write(", %s" % ((len(tmp_y))/NUMBER_OF_PACKETS))
            else:
                histogramData.write(", 1")
            histogramData.write(", %s" % (np.sum(tmp_y)/NUMBER_OF_PACKETS))

            missing_values = (NUMBER_OF_PACKETS - len(tmp_y))
            tmp_y.extend([-1] * (int(NUMBER_OF_PACKETS) - len(tmp_y)))
            n, bins, patches = plt.hist(tmp_y, bins=range(MISSING_DATA_BIN, NUMBER_OF_BINS + 1), normed=True, facecolor='green', alpha=0.5)
            for binValue in n:
                histogramData.write(", %s" % (binValue))

            histogramData.write("\n")
            # plt.show()
            plt.close()
            file.close()
    histogramData.close()
    print count


sys.exit(1)
