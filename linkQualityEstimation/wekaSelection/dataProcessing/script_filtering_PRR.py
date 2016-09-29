import os
import sys
import numpy as np
from numpy.polynomial import Polynomial
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
import matplotlib.mlab as mlab
import pandas as pd
PATH = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/wekaSelection/PRR/"
PATH_TO_FIGURE = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/wekaSelection/figures/PRR/"
PATH_TO_NEW_DATASET = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/weka/pythonExample/dataSet/"
NUMBER_OF_PACKETS = 301
NUMBER_OF_RECEIVERS = 28.0
RSSI = {}


def returnPDR(data, packet):
    ### Calculate PDR up to particular packet

    count = 0
    for seqNum in sorted(newFile[fileName], key=lambda k: int(k)):
        if int(seqNum) <= packet:
            count = count + 1.0
    return count / (packet + 1.0)


def initRSSI():
    for packet in range(0, NUMBER_OF_PACKETS+1):
        RSSI[packet] = []

for root, dirs, files in os.walk(PATH):
    print root
    x, y = [], []
    PRR = []
    RSSI_AVG = []
    fiveNumSummary = 0
    initRSSI()
    newFile = {}
    for file in files:
        print file
        key = file
        tmp_x, tmp_y = [], []
        if file.endswith(""):
            newFile[key] = {}
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    # RSSI limit to 90, filter few 250 values
                    if int(data[1]) <= 90:
                        tmp_x.append(int(data[0]))
                        tmp_y.append(int(data[1]))
                        RSSI[int(data[0])].append(int(data[1]))
                        newFile[key][data[0]] = int(data[1])
            file.close()
        x.extend(tmp_x)
        y.extend(tmp_y)
    # Calculate mean avarage RSSI values per receiver
    for i in range(0, NUMBER_OF_PACKETS + 1):
        RSSI_AVG.append(np.sum(RSSI[i])/NUMBER_OF_RECEIVERS)
        receivedPackets = x.count(i)
        PRR.append((receivedPackets * 1.0)/NUMBER_OF_RECEIVERS)

    if len(y) > 1:
        root = root.lstrip()
        tmp = root[len(PATH):]
        dir = tmp.split("/")
        name = dir[1].split("_")
            # Create directory path if it is missing
        if not os.path.exists(PATH_TO_FIGURE + dir[0]):
            os.makedirs(PATH_TO_FIGURE + dir[0])

        # Plot RSSI values of each packet
        # for i in range(0, NUMBER_OF_PACKETS + 1):
        #     for rssi in RSSI[i]:
        #         plt.scatter(rssi, PRR[i])

        # Data fit distribution
        # p = Polynomial.fit(RSSI_AVG, PRR, 5)
        # plt.plot(*p.linspace())

        # Plot RSSI_AVG values on x and PRR on y coordinate
        plt.scatter(RSSI_AVG, PRR)
        plt.xlabel("RSSI - mean AVG")
        plt.ylabel('PRR')

        plt.savefig(PATH_TO_FIGURE + dir[0] + "/" + name[1] + ".png")
        # plt.show()
        plt.close()

        if not os.path.exists(PATH_TO_NEW_DATASET + dir[0]):
            os.makedirs(PATH_TO_NEW_DATASET + dir[0])

        file = open(PATH_TO_NEW_DATASET + dir[0] + "/" + name[1] + ".arff", 'w')

        # Prepare header
        file.write("@RELATION transmitted \n")
        file.write("@ATTRIBUTE link     string\n")
        file.write("@ATTRIBUTE seqNumber    numeric\n")
        file.write("@ATTRIBUTE RSSI	numeric\n")
        file.write("@ATTRIBUTE PRR 	numeric\n")
        file.write("@ATTRIBUTE PDR	numeric\n")

        file.write("@DATA\n")
        for fileName in newFile:
            for seqNum in sorted(newFile[fileName], key=lambda k: int(k)):
                file.write("%s, %s, %s, %s, %s\n" % (fileName, seqNum, newFile[fileName][seqNum], PRR[int(seqNum)], returnPDR(newFile[fileName], int(seqNum))))
        file.close()

        # sys.exit(1)
