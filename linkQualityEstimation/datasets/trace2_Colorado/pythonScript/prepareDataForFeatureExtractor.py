import os
import sys
from shutil import rmtree
import pandas as pd


PATH_DATA = "../data/"
FEATURE_EXTRACTOR_DATASETS = "../../../featureGenerator/datasets/dataset-3-colorado_wifi/"
NUMBER_OF_PACKETS = 500
POWER = range(10, 21)   # range 10 to 20
MONITOR = range(1, 6)  # 5 monitors
ANTENNA_POSITION = ["up", "down", "left", "right"]
FILES = {"omni_16dbm": 500.0, "omni_variable_txpower": 200.0, "dir_variable_txpower": 200.0}
NUMBER_OF_BINS = 80
DATA = {}
NODES = []
tmpDir = ""
numberOfExperiments = 0


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


def progressBar(count, total, suffix=''):
    bar_len = 40
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()


# Create dataset directory
if os.path.exists(FEATURE_EXTRACTOR_DATASETS):
    rmtree(FEATURE_EXTRACTOR_DATASETS)
os.makedirs(FEATURE_EXTRACTOR_DATASETS)

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

            for pwr in POWER:
                for mnt in MONITOR:
                    # Filter empty records
                    NODES = DATA[pwr, mnt]
                    if len(NODES) >= 1:
                        print "\n"
                        print "Power level %s, monitor %s, links %s" % (pwr, mnt, len(NODES))
                        for id, node in enumerate(sorted(NODES)):
                            if tmpDir != directory:
                                numberOfExperiments += 1
                            progressBar(id, len(NODES) - 1, "Progress")
                            node = NODES[node]
                            experimentPath = FEATURE_EXTRACTOR_DATASETS + "experiment-" + str(numberOfExperiments) + "-" + str(directory)

                            if not os.path.exists(experimentPath):
                                tmpDir = directory
                                os.makedirs(experimentPath)

                            # Create csv file per link
                            # id = node that is transmitting the data
                            # mnt = monitor that is receiving the data
                            csvFile = experimentPath + "/trans-" + str(id) + "-recv-" + str(mnt) + "-pwr-" + str(pwr) + ".csv"
                            x, y = zip(*sorted(zip(node['seq'], node['rssi'])))
                            df = pd.DataFrame({"seq": x, "rssi": y})
                            # Keep colum order
                            df = df[['seq', 'rssi']]
                            df.to_csv(csvFile, index=False, header=True, cols=['seq', 'rssi'])
        print "\n"
        print "*************** DONE **************"
        # sys.exit(1)
