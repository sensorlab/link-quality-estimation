import os
import sys
import pandas as pd
from shutil import rmtree
from natsort import natsorted
import numpy as np

PATH = "../data/"
FEATURE_EXTRACTOR_DATASETS = "../../../featureGenerator/datasets/dataset-2-rutgers_wifi/"
NUMBER_OF_PACKETS = 300
RSSI_MAX = 127
RSSI_MIN = 0

number_experiment = 0
tmp_dir = ""

# Create dataset directory
if os.path.exists(FEATURE_EXTRACTOR_DATASETS):
    rmtree(FEATURE_EXTRACTOR_DATASETS)
os.makedirs(FEATURE_EXTRACTOR_DATASETS)

for root, dirs, files in natsorted(os.walk(PATH)):
    root = root.lstrip()
    print root
    tmp = root[len(PATH):]
    dir = tmp.split("/")
    for file in files:
        if file.endswith(""):
            x, y, z = [], [], []
            current_seq = 0
            previous_rssi = RSSI_MIN
            previous_seq = -1

            name = dir[1].split("_")
            from_node = name[1].replace("-", "_")
            to_node = str("node" + file[len("sdec"):]).replace("-", "_")
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    rssi = int(data[1])
                    seq = int(data[0])
                    if seq < NUMBER_OF_PACKETS and rssi <= RSSI_MAX and rssi >= RSSI_MIN:
                        # Interpolate
                        avg_rssi = np.mean((previous_rssi, rssi))
                        std_rssi = np.std((previous_rssi, rssi))
                        std_rssi = std_rssi if std_rssi > 0 else sys.float_info.min
                        difference = seq - previous_seq - 1
                        x.extend(range(previous_seq + 1, int(data[0])))
                        y.extend(np.random.normal(avg_rssi, std_rssi, size=difference))
                        z.extend(["false"] * difference)
                        
                        x.append(seq)
                        y.append(rssi)
                        z.append("true")
                        previous_seq = seq
                        previous_rssi = rssi
            # Interpolate
            difference = NUMBER_OF_PACKETS - previous_seq - 1
            avg_rssi = np.mean((previous_rssi, RSSI_MIN))
            std_rssi = np.std((previous_rssi, RSSI_MIN))
            std_rssi = std_rssi if std_rssi > 0 else sys.float_info.min
            x.extend(range(previous_seq + 1, NUMBER_OF_PACKETS))
            y.extend(np.random.normal(avg_rssi, std_rssi, size=difference))
            z.extend(["false"] * difference)

            file.close()


            # Create directory path if it is missing
            if tmp_dir != dir[0]:
                number_experiment += 1
            experiment_path = FEATURE_EXTRACTOR_DATASETS + "experiment-" + str(number_experiment) + "-noise_level_" + dir[0].replace("-", "_")
            if not os.path.exists(experiment_path):
                tmp_dir = dir[0]
                os.makedirs(experiment_path)

            # Create csv file per link
            csv_file = experiment_path + "/trans-" + from_node + "-recv-" + to_node + ".csv"
            print "trans-" + from_node + "-recv-" + to_node + ".csv"
            df = pd.DataFrame({"seq": x, "rssi": y, "received": z})
            # Keep colum order
            df = df[['seq', 'rssi', 'received']]
            df.to_csv(csv_file, index=False, header=True, cols=['seq', 'rssi', 'received'])
