import os
from matplotlib import pyplot as plt
import pandas as pd

PATH = "../data/"
PATH_TO_OUTPUT = "../output/per_link/"
NUMBER_OF_PACKETS = 300.0
RSSI_MAX = 127
RSSI_MIN = 0
NUMBER_OF_BINS = 40
MISSING_DATA_BIN = -1

print "Start per link calculation"
PRR = []
RSSI_MEAN = []
for root, dirs, files in os.walk(PATH):
    root = root.lstrip()
    print root
    tmp = root[len(PATH):]
    dir = tmp.split("/")
    for file in files:
        if file.endswith(""):
            x, y = [], []
            missing_values = 0

            name = dir[1].split("_")
            from_node = name[1]
            to_node = str("node" + file[len("sdec"):])
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
                RSSI_MEAN.append(sum(y) / (len(y) * 1.0))

                # Create directory path if it is missing
                if not os.path.exists(PATH_TO_OUTPUT + dir[0]):
                    os.makedirs(PATH_TO_OUTPUT + dir[0])

                five_num_summary = pd.Series(y)
                
                # Plot RSSI values vs seq number
                plt.plot(x, y)
                plt.xlabel("Packet sequence number")
                plt.ylabel('RSSI index')
                plt.savefig(PATH_TO_OUTPUT + dir[0] + "/time_" + from_node + "TO" + to_node + '.png')
                plt.close()
                
                # Add missing packets to y as invalid values for Atheros cards
                y.extend([MISSING_DATA_BIN] * int(missing_values))
                n, bins, patches = plt.hist(y, bins=range(-1, NUMBER_OF_BINS + 1), normed=True, histtype='stepfilled', facecolor='green', alpha=0.5)

                plt.xlabel("RSSI")
                plt.ylabel('Probability')
                plt.title("Link - %s to %s(trx level %s)" % (from_node, to_node, dir[0]))
                plt.savefig(PATH_TO_OUTPUT + dir[0] + "/" + from_node + "TO" + to_node + '.png')
                # plt.show()
                plt.close()

                # Calculate five numbers summary and store in a file
                print "---------------------"
                print "Number of missing values - %s \n" % (missing_values)
                print "Link - %s %s(trx level %s)" % (from_node, to_node, dir[0])
                print five_num_summary.describe()
                print (PATH_TO_OUTPUT + dir[0] + "/" + name[1])
                file = open(PATH_TO_OUTPUT + dir[0] + "/" + from_node + "TO" + to_node + '_5num.txt', 'w')
                file.write("Number of missing values - %s \n" % (missing_values))
                file.write(str(five_num_summary.describe()))
                file.close()

plt.scatter(RSSI_MEAN, PRR, c='blue', alpha=0.5)
plt.xlabel("average RSSI")
plt.ylabel('PRR')
plt.show()