import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
import matplotlib.mlab as mlab
import pandas as pd
import matplotlib.colors as colors
PATH = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/Trace_1/data/"
PATH_TO_FIGURE = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/Trace_1/figures/perLinkMissing/"
NUMBER_OF_PACKETS = 300.0
RSSI_MAX = 127
RSSI_MIN = 0
NUMBER_OF_BINS = 40
MISSING_DATA_BIN = -1
WINDOW_SIZE = 50.0


def calculateWindowParam(seqNumArray, RSSIArray):
    global PRR_WINDOW, RSSI_WINDOW
    tmpSeq = 0
    tmpSeqArray = []
    tmpRSSIArray = []
    # Add missing values in tmp arrays
    count = 0
    for seq, rssi in zip(seqNumArray, RSSIArray):
        count = count + 1
        diff = int(seq) - tmpSeq
        if diff > 1:
            tmpSeqArray.extend([-1] * (int(diff)-1))
            tmpRSSIArray.extend([0] * (int(diff)-1))
        tmpSeqArray.append(seq)
        tmpRSSIArray.append(rssi)
        tmpSeq = int(seq)
        # Check for last element
        if (count >= len(seqNumArray)) and (int(seq) < NUMBER_OF_PACKETS):
            tmpSeqArray.extend([-1] * int(NUMBER_OF_PACKETS-int(seq)-1))
            tmpRSSIArray.extend([0] * int(NUMBER_OF_PACKETS-int(seq)-1))
    # Slice and calculation
    print len(tmpRSSIArray)
    for i in range(1, int(NUMBER_OF_PACKETS/WINDOW_SIZE) + 1):
        windowSeqArray = tmpSeqArray[int((i-1)*WINDOW_SIZE):int(i*WINDOW_SIZE)]
        windowRSSIArray = tmpRSSIArray[int((i-1)*WINDOW_SIZE):int(i*WINDOW_SIZE)]
        receivedPackets = sum(x > -1 for x in windowSeqArray)
        PRR_WINDOW.append(receivedPackets/WINDOW_SIZE)
        if receivedPackets > 0:
            RSSI_WINDOW.append(sum(windowRSSIArray)/(WINDOW_SIZE*1.0))
        else:
            RSSI_WINDOW.append(0.0)

print "Start per link calculation"
PRR = []
RSSI_MEAN = []
PRR_WINDOW = []
RSSI_WINDOW = []
for root, dirs, files in os.walk(PATH):
    root = root.lstrip()
    tmp = root[len(PATH):]
    dir = tmp.split("/")
    for file in files:
        if file.endswith(""):
            print file
            x, y = [], []
            checkMissing = 0
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
                # Start preparing data for histogram
                PRR.append(len(y) / NUMBER_OF_PACKETS)
                RSSI_MEAN.append(sum(y) / WINDOW_SIZE* 1.0)
                calculateWindowParam(x, y)
                # Create directory path if it is missing
                if not os.path.exists(PATH_TO_FIGURE + dir[0]):
                    os.makedirs(PATH_TO_FIGURE + dir[0])

                fiveNumSummary = pd.Series(y)
                # Plot RSSI values vs seq number
                plt.plot(x, y)
                plt.xlabel("Packet sequence number")
                plt.ylabel('RSSI index')
                plt.savefig(PATH_TO_FIGURE + dir[0] + "/time_" + fromNode + "TO" + toNode + '.png')
                plt.close()
                # Add missing packets to y as invalid values for Atheros cards
                y.extend([MISSING_DATA_BIN] * int(missing_values))
                n, bins, patches = plt.hist(y, bins=range(-1, NUMBER_OF_BINS + 1), normed=True, histtype='stepfilled', facecolor='green', alpha=0.5)
                # y = mlab.normpdf(bins, fiveNumSummary.mean(), fiveNumSummary.std())
                # plt.plot(bins, y, 'r--')
                plt.xlabel("RSSI")
                # plt.xticks(range(0, max(y), 15), rotation=70)
                plt.ylabel('Probability')
                plt.title("Link - %s to %s(trx level %s)" % (fromNode, toNode, dir[0]))
                plt.savefig(PATH_TO_FIGURE + dir[0] + "/" + fromNode + "TO" + toNode + '.png')
                # plt.show()
                plt.close()

                # Calculate five numbers summary and store in a file

                #print "---------------------"
                #print "Number of missing values - %s \n" % (missing_values)
                #print "Link - %s %s(trx level %s)" % (fromNode, toNode, dir[0])
                #print fiveNumSummary.describe()
                #print (PATH_TO_FIGURE + dir[0] + "/" + name[1])
                file = open(PATH_TO_FIGURE + dir[0] + "/" + fromNode + "TO" + toNode + '_5num.txt', 'w')
                file.write("Number of missing values - %s \n" % (missing_values))
                file.write(str(fiveNumSummary.describe()))
                file.close()

plt.scatter(RSSI_MEAN, PRR, c='blue', alpha=0.5)
plt.xlabel("RSSI")
# plt.xticks(range(0, max(y), 15), rotation=70)
plt.ylabel('PRR')
plt.grid()
plt.show()
plt.close()
plt.scatter(RSSI_WINDOW, PRR_WINDOW, c='blue', alpha=0.5)
plt.xlabel("RSSI")
# plt.xticks(range(0, max(y), 15), rotation=70)
plt.ylabel('PRR')
plt.grid()
plt.show()
plt.close()
markersDEF = ['*', '+', 'x', 'p', '<', 'v', 's', 'x', '+', 's', 'o', '+']
colorsDEF = ["gold", "aqua", "red", "blue", "darkred", "green", "lime", "magenta", "orangered", "deeppink", "darkviolet", "black"]
for i, color in zip(range(1, 13), colors.cnames):
    print colorsDEF[i-1], markersDEF[i-1]
    print "RSSI"
    print RSSI_WINDOW[int((i-1)*10):int(i*10)]
    print "PRR"
    print PRR_WINDOW[int((i-1)*10):int(i*10)]
    plt.scatter(RSSI_WINDOW[int((i-1)*10):int(i*10)], PRR_WINDOW[int((i-1)*10):int(i*10)], c=colorsDEF[i-1], alpha=0.7, marker=markersDEF[i-1], s=50)
plt.show()
plt.close()
