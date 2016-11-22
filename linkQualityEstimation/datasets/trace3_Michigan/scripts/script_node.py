from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
import pandas as pd
from itertools import islice
import os

PATH_TO_DATA_FILE = "../data/css/Y.css"
PATH_TO_RESULTS = "../results/Y/nodes/"
MEASUREMENTS_PER_DEVICE = 13

if not os.path.exists(PATH_TO_RESULTS):
    os.makedirs(PATH_TO_RESULTS)

node_number = 0
file = open(PATH_TO_DATA_FILE, 'r')
while True:
    n_lines = list(islice(file, MEASUREMENTS_PER_DEVICE))
    if not n_lines:
        break

    y = []
    node_number += 1
    for line in n_lines:
        #ignore_leading = True
        for measurement in line.split(","):
            # Measurements are asynchronous, ignore leading zeros
            #if ignore_leading:
            #    if int(measurement) == 0:
            #        continue
            #    ignore_leading = False
            y.append(float(measurement))

    # Five numbers summary
    five_num_summary = pd.Series(y)
    SAVE_PATH = PATH_TO_RESULTS + "/node_" + str(node_number) + "_five_num.txt"
    file_five_num = open(SAVE_PATH, 'w')
    file_five_num.write(str(five_num_summary.describe())[:-15])
    file_five_num.close()

    # Histogram
    n, bins, patches = plt.hist(y, bins='auto', normed=1, facecolor='green', alpha=0.5)
    pdf = mlab.normpdf(bins, five_num_summary.mean(), five_num_summary.std())
    plt.plot(bins, pdf, 'r--')
    plt.xlabel("RSSI")
    plt.ylabel('Probability')
    plt.title("Node number - %d" % node_number)

    SAVE_PATH = PATH_TO_RESULTS + "/node_" + str(node_number) + ".png"
    plt.savefig(SAVE_PATH)
    #plt.show()
    plt.close()


file.close()
