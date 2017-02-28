import os
import numpy as np
from matplotlib import pyplot as plt

PATH = "../data/"
PATH_TO_OUTPUT = "../output/clustering/"
NUMBER_OF_PACKETS = 300.0
NUMBER_OF_BINS = 40
RSSI_MAX = 127
RSSI_MIN = 0
MISSING_DATA_BIN = -1

# Initalize files' content
def create_files():
    file_list = ["dbm0.arff", "dbm-5.arff", "dbm-10.arff", "dbm-15.arff", "dbm-20.arff"]
    if not os.path.exists(PATH_TO_OUTPUT):
        os.makedirs(PATH_TO_OUTPUT)
    for file in file_list:
        file = open(PATH_TO_OUTPUT + file, 'w')
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

count_invalid = 0
create_files()
for root, dirs, files in os.walk(PATH):
    x, y = [], []
    root = root.lstrip()
    tmp = root[len(PATH):]
    dir = tmp.split("/")

    if dir[0] == "":
        continue
    histogram_data = open(PATH_TO_OUTPUT + dir[0] + '.arff', 'a')
    print "Transmission power:", dir[0]

    for file in files:
        tmp_x, tmp_y = [], []
        if file.endswith(""):
            # Parse data
            name = dir[1].split("_")
            from_node = name[1]
            to_node = str("node" + file[len("sdec"):])
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    if int(data[1]) > RSSI_MAX:
                        count_invalid = count_invalid + 1
                    if int(data[1]) <= RSSI_MAX and int(data[1]) >= RSSI_MIN:
                        tmp_x.append(data[0])
                        tmp_y.append(int(data[1]))

            # Print data to files
            histogram_data.write("%s, %s, %s" % (from_node, to_node, (from_node + "TO" + to_node)))
            if len(tmp_y) <= NUMBER_OF_PACKETS:
                histogram_data.write(", %s" % ((len(tmp_y)) / NUMBER_OF_PACKETS))
            else:
                histogram_data.write(", 1")
            
            if len(tmp_y) > 0:
                avg_rssi = np.sum(tmp_y) / (len(tmp_y) * 1.0)
            else:
                avg_rssi = "?"
            histogram_data.write(", %s" % (avg_rssi))

            tmp_y.extend([-1] * (int(NUMBER_OF_PACKETS) - len(tmp_y)))
            n, bins, patches = plt.hist(tmp_y, bins=range(MISSING_DATA_BIN, NUMBER_OF_BINS + 1), normed=True, facecolor='green', alpha=0.5)
            for bin_value in n:
                histogram_data.write(", %s" % (bin_value))
            histogram_data.write("\n")

            plt.close()
            file.close()
    
    histogram_data.close()

print "Number of invalid values: " + str(count_invalid)