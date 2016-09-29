import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
import matplotlib.mlab as mlab
import pandas as pd
PATH = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/wekaSelection/PDR/node1-2/"
PATH_TO_FIGURE = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/wekaSelection/figures/PDR/"
CENTRAL_NODE = "node1-2"
NUMBER_OF_PACKETS = 300.0
NUMBER_OF_RECEIVERS = 2.0


def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')

for root, dirs, files in os.walk(PATH):
    print root
    x, y = [], []
    PDR = []
    RSSI_AVG = []
    RSSI = {}
    for file in files:
        key = file
        tmp_x, tmp_y = [], []
        if file.endswith(""):
            RSSI[key] = []
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    # RSSI limit to 90, filter few 250 values
                    if int(data[1]) <= 90:
                        tmp_x.append(int(data[0]))
                        tmp_y.append(int(data[1]))
                        RSSI[key].append(int(data[1]))
            file.close()
        x.extend(tmp_x)
        y.extend(tmp_y)
    if len(y) > 1:
        root = root.lstrip()
        tmp = root[len(PATH):]
        dir = tmp.split("/")
        name = dir[0]
        if not os.path.exists(PATH_TO_FIGURE):
            os.makedirs(PATH_TO_FIGURE)
        # Calculate mean avarage RSSI values per receiver
        transmittedPDR = []
        receivedPDR = []
        label = []
        for key in sorted(RSSI, key=lambda k: int(k.split("_")[0])):
            if "transmitted" in key:
                transmittedPDR.append(len(RSSI[key]) / NUMBER_OF_PACKETS)
                label.append(key[:(len(key)-len("_transmitted"))])
                print "transmitted"
                print key
            else:
                print key
                print "received"
                receivedPDR.append(len(RSSI[key]) / NUMBER_OF_PACKETS)
            # Plot RSSI values of each packet
            # for i in range(0, NUMBER_OF_PACKETS + 1):
            #     for rssi in RSSI[i]:
            #         plt.scatter(rssi, PRR[i])
            # Data fit distribution
            # p = Polynomial.fit(RSSI_AVG, PRR, 5)
            # plt.plot(*p.linspace())
        print receivedPDR
        print label
        ind = np.arange(len(label))  # the x locations for the groups
        width = 0.25       # the width of the bars
        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, transmittedPDR, width, color='g')
        rects2 = ax.bar(ind + width, receivedPDR, width, color='b')
        ax.legend((rects1[0], rects2[0]), ('recorded at node1-2', 'recorded at %s' % (name)))
        ax.set_xticks(ind + width)
        ax.set_xticklabels(label)
        autolabel(rects2)
        plt.xlabel("Link")
        plt.ylabel('PDR')
        plt.savefig(PATH_TO_FIGURE + name + '.png')
        plt.show()
        plt.clf()
        plt.close()
