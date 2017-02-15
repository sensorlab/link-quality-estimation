# Some parts of the script copied from Tomaz Solc (https://github.com/avian2)

import glob
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt



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
            
            packets_in_link[link_id].append(row)

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


n_links = len(packets_in_link)

f_out = open("./colorado_links.arff", "w")
f_out.write("@RELATION colorado_links\n\n")
f_out.write("@ATTRIBUTE rssi_avg NUMERIC\n@ATTRIBUTE rssi_std NUMERIC\n@ATTRIBUTE prr NUMERIC\n@ATTRIBUTE class {good,intermediate,bad}\n\n")
f_out.write("@DATA\n")

for i, (link_id, rows) in enumerate(packets_in_link.items()):
    
    n_received = len(rows)
    n_sent = expected_n_packets[link_id]
    
    prr = float(n_received)/n_sent
    
    monitor = link_id[6]
    mean_rssi = sum(row.rssi[monitor] for row in rows)/float(n_received)
    
    std_rssi = np.std([row.rssi[monitor] for row in rows])
    
    if prr > 0.9:
        label = "good"
    elif prr < 0.1:
        label = "bad"
    else:
        label = "intermediate"
    
    f_out.write(','.join(map(str, (mean_rssi, std_rssi, prr, label))) + "\n")

f_out.close()