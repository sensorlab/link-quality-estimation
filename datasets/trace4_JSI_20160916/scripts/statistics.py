import os
from natsort import natsorted
from sklearn import preprocessing
import pandas as pd
#import warnings
#warnings.filterwarnings("ignore", category=DeprecationWarning) 

PATH_TO_DATA = "../../../featureGenerator/datasets/dataset-4-JSI_sigfox_20160916/"

experiments = []
file_names = []
all_measurements = []

# Parse the data
for root, _, files in os.walk(PATH_TO_DATA):
	for file in natsorted(files):
		file_names.append((root.split("/")[-1], file))
		f = open(os.path.join(root, file), "r")
		rssi_array = []
		snr_array = []
		next(f) # Ignore the header
		for line in f:
			tokens = line.split(",")
			rssi = float(tokens[1])
			snr = float(tokens[2])
			rssi_array.append(rssi)
			snr_array.append(snr)
		experiments.append(rssi_array)
		all_measurements.extend(rssi_array)
		f.close()

# Normalize the data and print five number summaries for each link
min_max_scaler = preprocessing.MinMaxScaler(feature_range = (0, 10))
min_max_scaler.fit_transform(all_measurements)

for title, measurements in zip(file_names, experiments):
	print(title)
	five_num_summary = pd.Series(min_max_scaler.transform(measurements)).describe()
	print(five_num_summary)
