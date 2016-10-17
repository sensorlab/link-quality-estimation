import os
import sys
from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
import pandas as pd

PATH = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/Trace_2"
PATH_DATA = PATH + "/data/"
PATH_FIGURE = PATH + "/figures/perMonitor/"
NUMBER_OF_PACKETS = 500
POWER = range(10, 21)   # range 10 to 20
MONITOR = range(1, 6)  # 5 monitors
ANTENNA_POSITION = ["up", "down", "left", "right"]
RSSI = {}
NODES = []


def initRSSI():
    '''
    Initialize RSSI dict.
    '''
    for pwr in POWER:
        for mnt in MONITOR:
            RSSI[pwr, mnt] = []


for root, dirs, files in os.walk(PATH_DATA):
    directory = ""
    fiveNumSummary = 0
    print "Start"
    print "================="
    for file in files:
        initRSSI()
        NODES = []
        if file.endswith(".txt"):
            directory = file.strip(".txt")
            print file
            if not os.path.exists(PATH_FIGURE + directory):
                os.makedirs(PATH_FIGURE + directory)
            print directory
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                '''
                Add RSSI values per monitor
                Format: power level, monitor
                RSSI value: 6 to 10 index value in data array
                '''
                if str(data[0] + "_" + data[1]) not in NODES:
                    NODES.append(str(data[0] + "_" + data[1]))
                RSSI[int(data[4]), 1].append(int(data[6]))
                RSSI[int(data[4]), 2].append(int(data[7]))
                RSSI[int(data[4]), 3].append(int(data[8]))
                RSSI[int(data[4]), 4].append(int(data[9]))
                RSSI[int(data[4]), 5].append(int(data[10]))
            file.close()
            print "Number of nodes %s" % (len(NODES))
            # Start plotting and calculating 5 num summary
            print "Preparing histograms per Monitor and calculating 5 num summary."
            for pwr in POWER:
                for mnt in MONITOR:
                    # Filter empty records
                    if len(RSSI[pwr, mnt]) > 1:
                        fileName = "Monitor_%s_pwr_%s" % (mnt, pwr)
                        fiveNumSummary = pd.Series(RSSI[pwr, mnt])
                        n, bins, patches = plt.hist(RSSI[pwr, mnt], bins='auto', normed=True, facecolor='green', alpha=0.5)
                        y = mlab.normpdf(bins, fiveNumSummary.mean(), fiveNumSummary.std())
                        plt.plot(bins, y, 'r--')
                        plt.xlabel("RSSI (dBm)")
                        # plt.xticks(range(0, max(y), 15), rotation=70)
                        plt.ylabel('Normalized frequency of RSSI values')
                        plt.title("Monitor %s (Power level %s)" % (mnt, pwr))
                        # plt.show()
                        plt.savefig(PATH_FIGURE + directory + "/" + fileName + '.png')
                        plt.close()
                        # Calculate five numbers summary and store in a file
                        # print "---------------------"
                        # print "Monitor %s (Power level %s)" % (mnt, pwr)
                        # print fiveNumSummary.describe()
                        file = open(PATH_FIGURE + directory + "/" + fileName + ".txt", "w")
                        file.write(str(fiveNumSummary.describe()))
                        file.close()
        print root
        print "*****************************"
        # sys.exit(1)
