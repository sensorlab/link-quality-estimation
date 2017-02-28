# Some parts of the script copied from Tomaz Solc (https://github.com/avian2)

import glob
from collections import defaultdict

import numpy as np
import pandas as pd

import sys
import os

OUT_DIRECTORY = "../../../featureGenerator/datasets/dataset-5-colorado/"

class CURow():
    def __init__(self, line):
        fi = line.split()
    
        self.x = float(fi[0])    
        self.y = float(fi[1])

        self.dev = fi[2]
        self.ant = fi[3]

        self.pw = int(fi[4])

        self.seq = int(fi[5])

        self.rssi = map(float, fi[6:])


packets_in_link = defaultdict(list)

for dataset in glob.glob("../data/*.txt"):
    for line in open(dataset):
        row = CURow(line)
        
        for i, rssi in enumerate(row.rssi):
            link_id = (dataset, row.x, row.y, row.dev, row.ant, row.pw, i)
            
            packets_in_link[link_id].append((row.seq, rssi))

expected_n_packets = {}
for link_id in packets_in_link.keys():
    
    dataset = link_id[0]
    if 'omni_16dbm' in dataset:
        n = 500
    elif 'omni_variable_txpower' in dataset:
        n = 200
    elif 'dir_variable_txpower' in dataset:
        n = 200
    else:
        assert False
        
    expected_n_packets[link_id] = n

    packets_in_link[link_id].sort(key=lambda x:x[0])




# interpolate
for link_id in packets_in_link.keys():
    seq_list, rssi_list, received_list = [], [], []
    current_seq = 0
    
    rssi_min = min([packet[1] for packet in packets_in_link[link_id]]) # MIN rssi of the link
    previous_rssi = rssi_min
    previous_seq = -1

    for packet in packets_in_link[link_id]:
            rssi = packet[1]
            seq = packet[0]
            if seq < expected_n_packets[link_id]:
                avg_rssi = np.mean((previous_rssi, rssi))
                std_rssi = np.std((previous_rssi, rssi))
                std_rssi = std_rssi if std_rssi > 0 else sys.float_info.min
                difference = seq - previous_seq - 1
                seq_list.extend(range(previous_seq + 1, seq))
                rssi_list.extend(np.random.normal(avg_rssi, std_rssi, size=difference))
                received_list.extend(["false"] * difference)
                
                seq_list.append(seq)
                rssi_list.append(rssi)
                received_list.append("true")
                previous_seq = seq
                previous_rssi = rssi
    difference = expected_n_packets[link_id] - previous_seq - 1
    avg_rssi = np.mean((previous_rssi, rssi_min))
    std_rssi = np.std((previous_rssi, rssi_min))
    std_rssi = std_rssi if std_rssi > 0 else sys.float_info.min
    seq_list.extend(range(previous_seq + 1, expected_n_packets[link_id]))
    rssi_list.extend(np.random.normal(avg_rssi, std_rssi, size=difference))
    received_list.extend(["false"] * difference)

    experiment_path = OUT_DIRECTORY
    dataset = link_id[0]
    if 'omni_16dbm' in dataset:
        experiment_path += "experiment-1-omni_16dbm/"
    elif 'omni_variable_txpower' in dataset:
        experiment_path += "experiment-2-omni_variable_txpower/"
    elif 'dir_variable_txpower' in dataset:
        experiment_path += "experiment-3-dir_variable_txpower/"
    else:
        assert False
    
    if not os.path.exists(experiment_path):
        os.makedirs(experiment_path)

    file_path_name = experiment_path + '-'.join(map(str, link_id))[8:].replace(".", "_") + ".csv"
    print(file_path_name)

    columns = ['seq', 'rssi', 'received']
    df = pd.DataFrame({"seq": seq_list, "rssi": rssi_list, "received": received_list})
    df = df[columns]
    df.to_csv(file_path_name, index=False, header=True, cols=columns)
