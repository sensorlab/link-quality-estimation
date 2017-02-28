from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
import pandas as pd
import os

PATH_TO_DATA_FILE = "../data/css/Y.css"
PATH_TO_RESULTS = "../results/Y/unidirectional_links/"
NUMBER_SENSORS = 14

if not os.path.exists(PATH_TO_RESULTS):
    os.makedirs(PATH_TO_RESULTS)

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

    # Five numbers summary
    five_num_summary = pd.Series(y)
    SAVE_PATH = PATH_TO_RESULTS + "/unidirectional_link_" + str(node1) + "_" + str(node2) + "_five_num.txt"
    file_five_num = open(SAVE_PATH, 'w')
    file_five_num.write(str(five_num_summary.describe())[:-15])
    file_five_num.close()

    # Histogram
    n, bins, patches = plt.hist(y, bins='auto', normed=1, facecolor='green', alpha=0.5)
    pdf = mlab.normpdf(bins, five_num_summary.mean(), five_num_summary.std())
    plt.plot(bins, pdf, 'r--')
    plt.xlabel("RSSI")
    plt.ylabel('Probability')
    plt.title("Link - node %d to node %d" % (node1, node2))

    SAVE_PATH = PATH_TO_RESULTS + "/unidirectional_link_" + str(node1) + "_" + str(node2) + ".png"
    plt.savefig(SAVE_PATH)
    #plt.show()
    plt.close()


file.close()
