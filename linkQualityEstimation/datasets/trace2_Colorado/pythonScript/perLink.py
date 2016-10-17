import os
import sys
from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
import pandas as pd
import multiprocessing

PATH = "/home/ado/Desktop/eWINE_Paris_SC2_RSSI/traces/Trace_2"
PATH_DATA = PATH + "/data/"
PATH_FIGURE = PATH + "/figures/perLink/"
NUMBER_OF_PACKETS = 500
POWER = range(10, 21)   # range 10 to 20
MONITOR = range(1, 6)  # 5 monitors
ANTENNA_POSITION = ["up", "down", "left", "right"]
FILES = {"omni_16dbm": 500.0, "omni_variable_txpower": 200.0, "dir_variable_txpower": 200.0}
NUMBER_OF_BINS = 80
DATA = {}
NODES = []
TIME_GRAPH = True # Generate time graphs per link

def initRSSI():
    '''
    Initialize RSSI dict.
    '''
    for pwr in POWER:
        for mnt in MONITOR:
            DATA[pwr, mnt] = {}


def initDatasetPerNode():
    node = {}
    node["seq"] = []
    node["rssi"] = []
    return node


def plotTimeGraph(x, y, pathToFig, fileName):
    plt.cla()
    plt.plot(x, y, linewidth=0.5)
    plt.xlabel("Packet sequence number")
    plt.ylabel('RSSI (dBm)')
    plt.savefig(pathToFig + "/time/" + fileName + '.png', dpi=700)
    plt.close()


def progressBar(count, total, suffix=''):
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()

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
            print directory
            file = open(os.path.join(root, file), 'r')
            tmpNode = ""
            tmpAntenna = ""
            tmpSeq = 0
            for line in file:
                data = line.split()
                '''
                Add RSSI values per monitor
                Format: power level, monitor
                RSSI value: 6 to 10 index value in data array
                Seq number: 5 index value
                '''
                # Filter only selected antenna position
                if str(data[3]) in ANTENNA_POSITION:
                    nodeName = str(data[0] + "_" + data[1])
                    if tmpNode == nodeName and tmpAntenna != str(data[3]) and tmpAntenna != "":
                        tmpSeq = tmpSeq + FILES[directory]
                    for id in MONITOR:
                        # Check if node exists
                        if nodeName not in DATA[int(data[4]), id]:
                            DATA[int(data[4]), id][nodeName] = initDatasetPerNode()
                        node = DATA[int(data[4]), id][nodeName]
                        node["rssi"].append(int(data[id + 5]))
                        node["seq"].append(tmpSeq + int(data[5]))
                    if tmpNode != nodeName:
                        tmpSeq = 0
                    tmpNode = nodeName
                    tmpAntenna = str(data[3])
            file.close()

            # Start plotting and calculating 5 num summary
            print "Preparing histograms per Monitor and calculating 5 num summary."
            for pwr in POWER:

                for mnt in MONITOR:
                    # Filter empty records
                    NODES = DATA[pwr, mnt]
                    if len(NODES) >= 1:
                        pathToFig = PATH_FIGURE + directory + "/" + str(pwr) + "/" + str(mnt)
                        if not os.path.exists(pathToFig):
                            os.makedirs(pathToFig)
                            os.makedirs(pathToFig + "/time")
                        print "\n"
                        print "Power level %s, monitor %s, links %s" % (pwr, mnt, len(NODES))
                        for id, node in enumerate(sorted(NODES)):
                            progressBar(id, len(NODES) - 1, "Progress")
                            fileName = "Node_%s_toMonitor_%s_pwr_%s" % (id, mnt, pwr)
                            node = NODES[node]
                            fiveNumSummary = pd.Series(node['rssi'])
                            plt.cla()
                            n, bins, patches = plt.hist(node['rssi'], bins=range(-100, NUMBER_OF_BINS - 100), normed=True, histtype='stepfilled', facecolor='green', alpha=0.5)
                            # y = mlab.normpdf(bins, fiveNumSummary.mean(), fiveNumSummary.std())
                            # plt.plot(bins, y, 'r--')
                            plt.xlabel("RSSI (dBm)")
                            # plt.xticks(range(0, max(y), 15), rotation=70)
                            plt.ylabel('Normalized frequency of RSSI values')
                            plt.title("Monitor %s (Power level %s)" % (mnt, pwr))
                            # plt.show()
                            plt.savefig(pathToFig + "/" + fileName + '.png')
                            plt.close()
                            x, y = zip(*sorted(zip(node['seq'], node['rssi'])))
                            plt.figure(figsize=(10, 5))
                            # Calculate five numbers summary and store in a file
                            # print "---------------------"
                            # print "Monitor %s (Power level %s)" % (mnt, pwr)
                            # print fiveNumSummary.describe()
                            file = open(pathToFig + "/" + fileName + ".txt", "w")
                            totalNumberOfPackets = FILES[directory] + tmpSeq
                            file.write("Number of missing values: %s \n" % (totalNumberOfPackets - len(node['seq'])))
                            file.write(str(fiveNumSummary.describe()))
                            file.write("\n")
                            file.write("PRR: %s " % (100*len(node['seq'])/(totalNumberOfPackets)))
                            file.close()
                            if TIME_GRAPH:
                                plotTimeGraph(x, y, pathToFig, fileName)
        print root
        print "*****************************"
        # sys.exit(1)
