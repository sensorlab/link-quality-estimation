from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
import pandas as pd
import numpy as np
import os

PATH_TO_DATA_FILE = "../data/css/Y.css"
PATH_TO_RESULTS = "../results/Y/links_comparison_time/"
NUMBER_SENSORS = 14

if not os.path.exists(PATH_TO_RESULTS):
    os.makedirs(PATH_TO_RESULTS)

link_data = dict()
link_number = 0
file = open(PATH_TO_DATA_FILE, 'r')
for line in file:
    # Node numbering
    node1 = link_number // NUMBER_SENSORS + 1
    node2 = link_number % NUMBER_SENSORS + 1
    if node1 == node2:
        node2 += 1
        link_number += 2
    else:
        link_number += 1

    y = []
    #ignore_leading = True
    for measurement in line.split(","):
        # Measurements are asynchronous, ignore leading zeros
        #if ignore_leading:
        #    if float(measurement) == 0:
        #        continue
        #    ignore_leading = False
        y.append(float(measurement))

    link_data[(node1, node2)] = y

# Statistics and graphs for each pair of nodes
for i in range(1, NUMBER_SENSORS):
    for j in range(i + 1, NUMBER_SENSORS + 1):
        node1 = i
        node2 = j

        for link in range(2):
            data = link_data[(node1, node2)]

            # Graph
            x = np.arange(0, len(data) / 2 + 0.5, 0.5)
            if link == 0:
                plt.plot(x, data, 'r', label=str(node1) + "-" + str(node2))
            else:
                plt.plot(x, data, 'g', label=str(node1) + "-" + str(node2))


            node1, node2 = node2, node1

        plt.xlabel("Seconds")
        plt.ylabel('RSSI')
        plt.title("Link - node %d and node %d" % (node1, node2))
        plt.legend(loc='upper left')

        SAVE_PATH = PATH_TO_RESULTS + "/comparison_time_link_" + str(node1) + "_" + str(node2) + ".png"
        plt.savefig(SAVE_PATH)
        #plt.show()
        plt.close()

file.close()
