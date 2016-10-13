import os
import numpy as np
import pandas as pd
from natsort import natsorted
import json
import matplotlib.pyplot as plt


PATH_TO_DATA = "/home/ijs/Desktop/eWINE_JSI_sigfox/data/"
PATH_TO_OUTPUT = "/home/ijs/Desktop/eWINE_JSI_sigfox/output/"

for root, _, files in os.walk(PATH_TO_DATA):
	for file in files:
		if not file.endswith(".json"):
			continue

		rssi_array = []
		received = []
		print(file)
		f = open(PATH_TO_DATA + file, "r")
		messages = json.loads(f.read())
		for message in messages:
			if "rx" in message.keys():
				rssi = message["rx"]["rssi"]
				rssi_array.append(float(rssi))
				received.append(1)
			else:
				received.append(0)
		f.close()

		plt.plot(range(len(rssi_array)), rssi_array, ".")
		#plt.ylim(ymin=0)
		plt.ylabel('RSSI')
		plt.xlabel('Packet number')
		#plt.title(file)
		plt.show()