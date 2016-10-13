import os
import numpy as np
import pandas as pd
from natsort import natsorted
from sklearn import preprocessing
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

PATH_TO_DATA = "/home/ijs/Desktop/eWINE_JSI_sigfox/data_transformed/"
PATH_TO_OUTPUT = "/home/ijs/Desktop/eWINE_JSI_sigfox/output/"

experiments = []
file_names = []
all_measurements = []
for root, _, files in os.walk(PATH_TO_DATA):
	for file in natsorted(files):
		print(file)
		file_names.append(file)
		f = open(os.path.join(root, file), "r")
		rssi_array = []
		snr_array = []
		for line in f:
			tokens = line.split(" ")
			rssi = float(tokens[1])
			snr = float(tokens[2])
			rssi_array.append(rssi)
			snr_array.append(snr)
		experiments.append(rssi_array)
		all_measurements.extend(rssi_array)
		f.close()

min_max_scaler = preprocessing.MinMaxScaler(feature_range = (0, 10))
min_max_scaler.fit_transform(all_measurements)
#scaler = preprocessing.StandardScaler().fit(np.array(all_measurements).reshape(1, -1))
for title, measurements in zip(file_names, experiments):
	print(title)
	#print(min_max_scaler.transform(measurements))
	five_num_summary = pd.Series(min_max_scaler.transform(measurements)).describe()
	print(five_num_summary)
