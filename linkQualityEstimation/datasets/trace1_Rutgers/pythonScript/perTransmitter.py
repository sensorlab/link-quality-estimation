import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
import matplotlib.mlab as mlab
import pandas as pd
PATH = "../data/"
PATH_TO_FIGURE = "../figures/perLink/""
NUMBER_OF_PACKETS = 300
RSSI_MAX = 127
RSSI_MIN = 0
NUMBER_OF_BINS = 40
MISSING_DATA_BIN = -1

for root, dirs, files in os.walk(PATH):
    x, y = [], []
    missing_values = 0
    fiveNumSummary = 0
    print "Start per transmitter calculation"
    for file in files:
        print file
        tmp_x, tmp_y = [], []
        if file.endswith(""):
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    if int(data[0]) < NUMBER_OF_PACKETS and int(data[1]) <= RSSI_MAX and int(data[1]) >= RSSI_MIN:
                        tmp_x.append(data[0])
                        tmp_y.append(int(data[1]))
            file.close()
        y.extend(tmp_y)

        if tmp_y >= 0:
            missing_values = missing_values + (NUMBER_OF_PACKETS - len(tmp_y))
    if len(y) > 1:
        # Start preparing data for histogram
        root = root.lstrip()
        tmp = root[len(PATH):]
        dir = tmp.split("/")
        name = dir[1].split("_")
        # Create directory path if it is missing
        if not os.path.exists(PATH_TO_FIGURE + dir[0]):
            os.makedirs(PATH_TO_FIGURE + dir[0])
        # plt.hist(y, 10, facecolor='green', alpha=0.7, histtype='bar', rwidth=0.8)
        #p, x = np.histogram(y, bins='auto')  # bin it into n = N/10 bins
        #x = x[:-1] + (x[1] - x[0])/2    # convert bin edges to centers
        #f = UnivariateSpline(x, p, s=10)
        #plt.plot(x, f(x), 'r--')
        #plt.hist(y, bins='auto', facecolor='green', alpha=0.7, histtype='bar', rwidth=0.8)
        fiveNumSummary = pd.Series(y)
        # Add missing packets to y as invalid values for Atheros cards
        y.extend([MISSING_DATA_BIN] * int(missing_values))
        n, bins, patches = plt.hist(y, bins=range(-1, NUMBER_OF_BINS + 1), normed=True, histtype='stepfilled', facecolor='green', alpha=0.5)
        # y = mlab.normpdf(bins, fiveNumSummary.mean(), fiveNumSummary.std())
        # plt.plot(bins, y, 'r--')
        plt.xlabel("RSSI")
        # plt.xticks(range(0, max(y), 15), rotation=70)
        plt.ylabel('Probability')
        plt.title("Transmitter - %s (noise level %s)" % (name[1], dir[0]))
        plt.savefig(PATH_TO_FIGURE + dir[0] + "/" + name[1] + '.png')
        # plt.show()
        plt.close()

        # Calculate five numbers summary and store in a file

        print "---------------------"
        print "Number of missing values - %s \n" % (missing_values)
        print "Transmitter - %s (trx level %s)" % (name[1], dir[0])
        print fiveNumSummary.describe()
        print (PATH_TO_FIGURE + dir[0] + "/" + name[1])
        file = open(PATH_TO_FIGURE + dir[0] + "/" + name[1] + '_5num.txt', 'w')
        file.write("Number of missing values - %s \n" % (missing_values))
        file.write(str(fiveNumSummary.describe()))
        file.close()
        # sys.exit(1)
