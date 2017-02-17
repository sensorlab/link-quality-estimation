import json
import matplotlib.pyplot as plt


PATH_TO_DATA = "../data/sfxlib_norep_randfreq_randgain.json"

GAIN_RANGE = 30
NUM_BINS = 30

gain_step = float(GAIN_RANGE) / NUM_BINS

received = {}
total = {}
snr_array = {}
rssi_array = {}

# Initialize each bin
for i in range(NUM_BINS):
	received[i] = 0
	total[i] = 0
	snr_array[i] = []
	rssi_array[i] = []

f = open(PATH_TO_DATA, "r")
messages = json.loads(f.read())

# Fill the bins
for message in messages:
	gain = message["tx"]["gain"] * -1
	if gain == GAIN_RANGE:
		key = NUM_BINS - 1
	else:
		key = int(gain // gain_step)
	if "rx" in message.keys():
		snr = message["rx"]["snr"]
		rssi = message["rx"]["rssi"]
		rssi_array[key].append(float(rssi))
		snr_array[key].append(float(snr))
		received[key] += 1
	total[key] += 1
f.close()

# Calculate the average of each bin
avg_rssi = []
avg_snr = []
prr = []
for i in range(NUM_BINS):
	avg_rssi.append(sum(rssi_array[i]) / len(rssi_array[i]))
	avg_snr.append(sum(snr_array[i]) / len(snr_array[i]))
	prr.append(float(received[i]) / total[i])

# Plot
plt.plot(range(0, -NUM_BINS, -1), avg_snr)
plt.ylim(ymin=7, ymax=12)
plt.ylabel('SNR')
plt.xlabel('Gain (dB)')
plt.show()