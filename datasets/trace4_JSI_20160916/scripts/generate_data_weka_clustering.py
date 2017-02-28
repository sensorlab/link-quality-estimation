import os
import json
import matplotlib.pyplot as plt


PATH_TO_DATA = "../data/"
PATH_TO_OUTPUT = "./"
WINDOW = 100

prr_array = []
rssi_array = []

for root, _, files in os.walk(PATH_TO_DATA):
	for file in files:
		# Ignore the randgain experiments
		if "randgain" in file or not file.endswith(".json") or not "sfxlib" in file:
			continue
		print(file)
		f = open(os.path.join(root, file), "r")
		messages = json.loads(f.read())
		i = 0
		received = 0
		total = 0
		tmp_rssi = 0
		# Calculate average RSSI per window and corresponding PRR
		for message in messages:
			i += 1
			total += 1
			if "rx" in message.keys():
				avg_snr = message["rx"]["avgSnr"]
				snr = message["rx"]["snr"]
				time = message["rx"]["time"]
				rssi = message["rx"]["rssi"]
				attenuator = message["tx"]["attenuator"]
				gain = message["tx"]["gain"]
				received += 1
				tmp_rssi += float(rssi)
			if i % WINDOW == 0:
				prr = float(received) / total
				avg_rssi = tmp_rssi / received
				prr_array.append(prr)
				rssi_array.append(avg_rssi)

				received = 0
				total = 0
				tmp_rssi = 0
		f.close()

# Print everything to an .arff file
f_out = open(PATH_TO_OUTPUT + "weka_clustering.arff", "w")
f_out.write("@RELATION sigfox\n\n")
f_out.write("@ATTRIBUTE rssi NUMERIC\n@ATTRIBUTE prr NUMERIC\n\n")
f_out.write("@DATA\n")
for rssi, prr in zip(rssi_array, prr_array):
	f_out.write(str(rssi) + "," + str(prr) + "\n")
f_out.close()

# Plot PRR versus average RSSI
plt.plot(rssi_array, prr_array, ".")
plt.ylim(ymax=1.05, ymin=0)
plt.ylabel('PRR')
plt.xlabel('RSSI')
plt.show()