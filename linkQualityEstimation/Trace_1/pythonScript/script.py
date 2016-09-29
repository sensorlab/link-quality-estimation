import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
import pandas as pd
PATH = "~/Desktop/eWINE_Paris_SC2_RSSI/Trace_1/data/"
PATH_TO_FIGURE = "~/Desktop/eWINE_Paris_SC2_RSSI/Trace_1/figures/"
NUMBER_OF_PACKETS = 300
binwidth = 250
for root, dirs, files in os.walk(PATH):
    x, y = [], []
    missing_values = 0
    for file in files:
        tmp_x, tmp_y = [], []
        if file.endswith(""):
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    tmp_x.append(data[0])
                    tmp_y.append(int(data[1]))
            file.close()
        # Add missing packets per file
        y.extend(tmp_y)
        # Filter empty files
        if tmp_y > 0:
            missing_values = missing_values + (NUMBER_OF_PACKETS - len(tmp_y))
            y.extend([255] * (NUMBER_OF_PACKETS - len(tmp_y)))
    if len(y) > 1:
        # Start preparing data for histogram
        root = root.lstrip()
        tmp = root[len(PATH):]
        dir = tmp.split("/")
        name = dir[1].split("_")
        # Create directory path if it is missing
        if not os.path.exists(PATH_TO_FIGURE + dir[0]):
            os.makedirs(PATH_TO_FIGURE + dir[0])
        plt.hist(y, 50, facecolor='green', alpha=0.7, histtype='bar', rwidth=0.8)

        plt.xlabel("RSSI")
        plt.ylabel('Frequency')
        plt.title("Transmitter - %s (noise level %s)" % (name[1], dir[0]))
        plt.savefig(PATH_TO_FIGURE + dir[0] + "/" + name[1] + '.png')
        # plt.show()
        plt.close()

        # Calculate five numbers summary and store in a file
        fiveNumSummary = pd.Series(y)
        print "---------------------"
        print "Number of missing values - %s \n" % (missing_values)
        print "Transmitter - %s (noise level %s)" % (name[1], dir[0])
        print fiveNumSummary.describe()
        print (PATH_TO_FIGURE + dir[0] + "/" + name[1])
        file = open(PATH_TO_FIGURE + dir[0] + "/" + name[1] + '_5num.txt', 'w')
        file.write("Number of missing values - %s \n" % (missing_values))
        file.write(str(fiveNumSummary.describe()))
        file.close()
        # sys.exit(1)
