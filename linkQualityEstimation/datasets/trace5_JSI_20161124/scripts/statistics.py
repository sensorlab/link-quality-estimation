# Some parts of the script copied from Tomaz Solc (https://github.com/avian2)

import json
import pandas as pd
from matplotlib.pyplot import *
from numpy import *
from sklearn import preprocessing
from collections import defaultdict
from scipy.special import betaincinv

# Parse data
data = json.load(open("../data/sfxlib_norep_30att.json"))
pkts_per_link = defaultdict(list)

for campaign in data['campaigns']:
    for pkt in campaign['packets']:
        link_id = (campaign['location'], pkt['tx']['pga_gain'])
        pkts_per_link[link_id].append(pkt)


N = 100
for link_id, pkts in pkts_per_link.items():
    assert len(pkts) == N

all_rssi = []
for link_id, pkts in pkts_per_link.items():
    all_rssi.extend([float(pkt['rx']['rssi']) for pkt in pkts if 'rx' in pkt])

# Normalize the rssi values
min_max_scaler = preprocessing.MinMaxScaler(feature_range = (0, 10))
min_max_scaler.fit_transform(all_rssi)

# Print five number summary and PRR
for link_id, pkts in pkts_per_link.items():
    
    n_tx = len(pkts)
    n_rx = sum('rx' in pkt for pkt in pkts)

    prr_mle = n_rx / float(n_tx)

    rssi = [float(pkt['rx']['rssi']) for pkt in pkts if 'rx' in pkt]
    five_num_sum = pd.Series(min_max_scaler.transform(rssi)).describe()
    print("\nLocation:" + str(link_id[0]) + "\nGain:" + str(link_id[1]) + \
        "\nPRR: " + str(prr_mle) + "\n" + str(five_num_sum))

# Calculate PRR for all links
Pconf = 0.99
prr_per_link = {}

for link_id, pkts in pkts_per_link.items():
    
    n_tx = len(pkts)
    n_rx = sum('rx' in pkt for pkt in pkts)
    
    N1 = float(n_rx)
    N0 = float(n_tx - n_rx)
        
    prr_min = betaincinv(N1+1, N0+1, (1. - Pconf)/2.)
    prr_max = betaincinv(N1+1, N0+1, (1. + Pconf)/2.)
    prr_mle = N1 / (N0 + N1)
        
    prr_per_link[link_id] = array([prr_mle, prr_min, prr_max])

# Plot PRR versus transmission gain
ll_prr = []

for campaign in range(4):
    l_gain = []
    l_prr = []

    for link_id in sorted(prr_per_link.keys()):
        if link_id[0] == campaign:
            l_gain.append( link_id[1] - 30)
            l_prr.append( prr_per_link[link_id] )
            
    l_prr = array(l_prr)
    ll_prr.append(l_prr)
            
    errorbar(l_gain, l_prr[:,0], yerr=[l_prr[:,0] - l_prr[:,1], l_prr[:,2]-l_prr[:,0]], fmt='o-', label='loc %d' % campaign)
    
ll_prr = array(ll_prr)
    
axis([-35, 5, 0, 1])
xlabel("transmit gain [dB]")
ylabel("PRR")
legend(loc="lower right")
title("%.0f%% confidence interval, N per estimate = %d" % (Pconf*100, N))
grid()
show()
clf()

# Calculate min/max/avg rssi per link
rssi_per_link = {}

for link_id, pkts in pkts_per_link.items():
    
    rssi = [float(pkt['rx']['rssi']) for pkt in pkts if 'rx' in pkt]
    
    rssi_per_link[link_id] = [
        mean(rssi),
        min(rssi),
        max(rssi)
    ]

# Plot RSSI versus transmission gain
ll_rssi = []

for campaign in range(4):
    l_gain = []
    l_rssi = []

    for link_id, rssi in sorted(rssi_per_link.items()):
        if link_id[0] == campaign:
            l_gain.append( link_id[1] - 30)
            l_rssi.append( rssi )
            
    l_rssi = array(l_rssi)
    ll_rssi.append(l_rssi)
            
    errorbar(l_gain, l_rssi[:,0], yerr=[l_rssi[:,0]-l_rssi[:,1], l_rssi[:,2]-l_rssi[:,0]], fmt='o-', label='loc %d' % campaign)
    
ll_rssi = array(ll_rssi)
    
axis([None, None, None, None])
xlabel("PGA gain [dB]")
ylabel("RSSI [dBm]")
legend(loc="lower right")
grid()
show()
clf()

# Plot RSSI versus PRR
for campaign in range(4):
    l_rssi = ll_rssi[campaign]
    l_prr = ll_prr[campaign]
    
    errorbar(l_rssi[:,0], l_prr[:,0], 
             xerr=[l_rssi[:,0]-l_rssi[:,1], l_rssi[:,2]-l_rssi[:,0]],
             yerr=[l_prr[:,0]-l_prr[:,1], l_prr[:,2]-l_prr[:,0]],
             fmt='o', label='loc %d' % campaign)
    
xlabel("RSSI [dBm]")
ylabel("PRR [%]")
legend(loc="lower right")
axis([None, None, 0, 1])
grid()
show()