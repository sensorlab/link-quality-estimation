import os
import json
import matplotlib.pyplot as plt


PATH_TO_DATA = "../data/"

for root, _, files in os.walk(PATH_TO_DATA):
	for file in files:
		if not file.endswith(".json") or not "sfxlib" in file:
			continue

		# Get RSSI of every packet
		rssi_array = []
		print(file)
		f = open(PATH_TO_DATA + file, "r")
		messages = json.loads(f.read())
		for message in messages:
			if "rx" in message.keys():
				rssi = message["rx"]["rssi"]
				rssi_array.append(float(rssi))

		f.close()

		# Plot RSSI of all packets for one link
		plt.plot(range(len(rssi_array)), rssi_array, ".")
		plt.ylabel('RSSI')
		plt.xlabel('Packet number')
		plt.title(file)
		plt.show()