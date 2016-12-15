from collections import defaultdict
import json
import numpy as np
import os

OUTPATH = "sigfox_dataset_20161124"

def load_pkts(tx_log, rx_log):
	packets = {}

	for line in open(tx_log):
		p = json.loads(line)
		p['attenuator'] = 0.
		packets[p['data']] = {'tx': p}

		del p['was_sent']

	for line in open(rx_log):
		p = json.loads(line)

		del p['lat']
		del p['lng']

		packets[p['data']]['rx'] = p

	packets_sorted = packets.values()
	packets_sorted.sort(key=lambda p: p['tx']['data'])

	return packets_sorted

def process_campaign():
	CAMPAIGN = OUTPATH + "/sfxlib_norep_30att"
	RAW_PATH = "raw/*_log_ijs_meritve_20161124"

	pkts = load_pkts(RAW_PATH.replace("*","tx"), RAW_PATH.replace("*","rx"))

	for pkt in pkts:
		pkt['tx']['attenuator'] = -30.

		assert 'frequency' not in pkt['tx']
		assert len(pkt['tx']['tx_frequency_list']) == 1

		pkt['tx']['frequency'] = pkt['tx']['tx_frequency_list'][0]
		del pkt['tx']['tx_frequency_list']

	rv = sort_by_campaign(pkts)

	f = open(CAMPAIGN + ".json", 'w')
	json.dump(rv, f, indent=4)
	f.close()

def sort_by_campaign(pkts):

	campaigns = defaultdict(list)

	for pkt in pkts:
		serial = int(pkt['tx']['data'], 16)

		campaign = serial / 5000

		campaigns[campaign].append(pkt)

	rv = {
		'campaigns': []
	}

	for n, pkts in campaigns.items():
		rv['campaigns'].append(
			{ 'location': n,
			'packets': pkts }
		)

	return rv

def main():
	process_campaign()

main()
