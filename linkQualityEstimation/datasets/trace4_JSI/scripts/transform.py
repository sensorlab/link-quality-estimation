import os
import json
import datetime
from natsort import natsorted

PATH_TO_DATA = "../data/"
PATH_TO_OUTPUT = "../data_feature_gen/"

experiment_no = 0
for root, _, files in os.walk(PATH_TO_DATA):
	for file in natsorted(files):
		if not file.endswith(".json"):
			continue
		print(file)
		directory = PATH_TO_OUTPUT + "experiment-" + str(experiment_no) + "-" + file.replace(".json", "")
		if not os.path.exists(directory):
			os.makedirs(directory)
		out_file_name = "trans-0-recv-1.csv" 
		f_out = open(os.path.join(PATH_TO_OUTPUT, directory, out_file_name), "w")
		seqno = 0
		f = open(os.path.join(root, file), "r")
		f_out.write("seq,rssi,snr,avg_snr,timestamp,attenuator,gain\n")
		messages = json.loads(f.read())
		for message in messages:
			#print("-")
			if "rx" in message.keys():
				avg_snr = message["rx"]["avgSnr"]
				snr = message["rx"]["snr"]
				time = message["rx"]["time"]
				rssi = message["rx"]["rssi"]
				attenuator = message["tx"]["attenuator"]
				gain = message["tx"]["gain"]
				f_out.write(str(seqno) + "," + rssi + "," + snr + "," + avg_snr + "," + time + "," + str(attenuator) + "," + str(gain) + "\n")
				#print(datetime.datetime.fromtimestamp(int(message["rx"]["time"])).strftime('%Y-%m-%d %H:%M:%S'))
			seqno += 1
		f.close()
		f_out.close()
		experiment_no += 1