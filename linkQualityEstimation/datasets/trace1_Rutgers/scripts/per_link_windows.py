import os
from matplotlib import pyplot as plt
import matplotlib.colors as colors

PATH = "../data/"
NUMBER_OF_PACKETS = 300.0
RSSI_MAX = 127
RSSI_MIN = 0
WINDOW_SIZE = 50.0


def calculate_window_param(seq_num_array, rssi_array):
    global PRR_WINDOW, RSSI_WINDOW
    tmp_seq = 0
    tmp_seq_array = []
    tmp_rssi_array = []
    # Add missing values in tmp arrays
    count = 0
    for seq, rssi in zip(seq_num_array, rssi_array):
        count = count + 1
        diff = int(seq) - tmp_seq
        if diff > 1:
            tmp_seq_array.extend([-1] * (int(diff)-1))
            tmp_rssi_array.extend([0] * (int(diff)-1))
        tmp_seq_array.append(seq)
        tmp_rssi_array.append(rssi)
        tmp_seq = int(seq)
        # Check for last element
        if (count >= len(seq_num_array)) and (int(seq) < NUMBER_OF_PACKETS):
            tmp_seq_array.extend([-1] * int(NUMBER_OF_PACKETS-int(seq)-1))
            tmp_rssi_array.extend([0] * int(NUMBER_OF_PACKETS-int(seq)-1))
    # Slice and calculation
    for i in range(1, int(NUMBER_OF_PACKETS / WINDOW_SIZE) + 1):
        window_seq_array = tmp_seq_array[int((i-1) * WINDOW_SIZE):int(i * WINDOW_SIZE)]
        window_rssi_array = tmp_rssi_array[int((i-1) * WINDOW_SIZE):int(i * WINDOW_SIZE)]
        received_packets = sum(x > -1 for x in window_seq_array)
        PRR_WINDOW.append(received_packets / WINDOW_SIZE)
        if received_packets > 0:
            RSSI_WINDOW.append(sum(window_rssi_array) / (len(window_rssi_array) * 1.0))
        else:
            RSSI_WINDOW.append(0.0)


PRR_WINDOW = []
RSSI_WINDOW = []
for root, dirs, files in os.walk(PATH):
    for file in files:
        if file.endswith(""):
            print file
            x, y = [], []
            file = open(os.path.join(root, file), 'r')
            for line in file:
                data = line.split()
                if len(data) > 1:
                    if int(data[0]) < NUMBER_OF_PACKETS and int(data[1]) <= RSSI_MAX and int(data[1]) >= RSSI_MIN:
                        x.append(data[0])
                        y.append(int(data[1]))
            file.close()

            if len(y) > 0:
                calculate_window_param(x, y)

# Plot windowed RSSI vs windowed PRR
plt.scatter(RSSI_WINDOW, PRR_WINDOW, c='blue', alpha=0.5)
plt.xlabel("RSSI")
plt.ylabel('PRR')
plt.grid()
plt.show()

# Plot
markers_DEF = ['*', '+', 'x', 'p', '<', 'v', 's', 'x', '+', 's', 'o', '+']
colors_DEF = ["gold", "aqua", "red", "blue", "darkred", "green", "lime", "magenta", "orangered", "deeppink", "darkviolet", "black"]
for i, color in zip(range(1, 13), colors.cnames):
    plt.scatter(RSSI_WINDOW[int((i-1)*10):int(i*10)], PRR_WINDOW[int((i-1)*10):int(i*10)], c=colors_DEF[i-1], alpha=0.7, marker=markers_DEF[i-1], s=50)
plt.show()