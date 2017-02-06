import os
import json
import datetime
from natsort import natsorted
from collections import defaultdict
import numpy as np
import sys
import pandas as pd

PATH_TO_DATA = "../data/"
PATH_TO_OUTPUT = "../data_feature_gen/"
TX_ATTRIBUTES =  ["timestamp", "attenuator", "pga_gain"]
RX_ATTRIBUTES = ["rssi", "snr", "avgSnr"]
NUMBER_PACKETS = 100

for root, _, files in os.walk(PATH_TO_DATA):    
    for file in natsorted(files):
        if not file.endswith(".json"):
            continue
        
        print(file)
        
        directory = PATH_TO_OUTPUT + "experiment-1-" + file.replace(".json", "")
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        f = open(os.path.join(root, file), "r")
        
        data = json.loads(f.read())
        packets_per_link = defaultdict(list)
        for campaign in data['campaigns']:
            for packet in campaign['packets']:
                link_id = (campaign['location'], packet['tx']['pga_gain'])
                packets_per_link[link_id].append(packet)
        
        min_value = {}
        previous_value = {}
        values = {}

        for link_id, packets in packets_per_link.items():
            
            for attribute in TX_ATTRIBUTES + RX_ATTRIBUTES:
                if attribute in RX_ATTRIBUTES:
                    min_value[attribute] = min([float(packet['rx'][attribute]) for packet in packets if 'rx' in packet])
                    previous_value[attribute] = min_value[attribute]
                values[attribute] = []
            
            gap = 0
            received = []
            
            for packet in packets:
                tx = packet['tx']
                
                if 'rx' in packet:
                    rx = packet['rx']
                    received.append(True)

                    if gap > 0:
                        for attribute in RX_ATTRIBUTES:
                            avg_value = np.mean((previous_value[attribute], float(rx[attribute])))
                            std_value = np.std((previous_value[attribute], float(rx[attribute])))
                            std_value = std_value if std_value > 0 else sys.float_info.min
                            values[attribute].extend(np.random.normal(avg_value, std_value, size=gap))
                        gap = 0

                    for attribute in RX_ATTRIBUTES:
                        previous_value[attribute] = float(rx[attribute])
                        values[attribute].append(float(rx[attribute]))
                else:
                    received.append(False)
                    gap += 1

                for attribute in TX_ATTRIBUTES:
                    values[attribute].append(float(tx[attribute]))

            if gap > 0:
                for attribute in RX_ATTRIBUTES:
                    avg_value = np.mean((previous_value[attribute], min_value[attribute]))
                    std_value = np.std((previous_value[attribute], min_value[attribute]))
                    std_value = std_value if std_value > 0 else sys.float_info.min
                    
                    values[attribute].extend(np.random.normal(avg_value, std_value, size=gap))

            file_out_name = directory + "/trans-0-recv-1-location-" + str(link_id[0]) + "-pga_gain-" +  str(link_id[1]) + ".csv"
            
            values['received'] = received
            values['seq'] = range(NUMBER_PACKETS)
            
            data_frame = pd.DataFrame(values)
            columns = sorted(values)
            data_frame = data_frame[columns]
            data_frame.to_csv(file_out_name, index=False, header=True, cols=columns)

        f.close()