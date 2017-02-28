import json
from math import log10

OUTPATH = "sigfox_dataset_20160916"

def load_pkts(tx_log, rx_log):
	packets = {}

	for line in open(tx_log):
		p = json.loads(line)
		p['attenuator'] = 0.
		packets[p['data']] = {'tx': p}

	for line in open(rx_log):
		p = json.loads(line)

		del p['lat']
		del p['lng']

		packets[p['data']]['rx'] = p

	packets_sorted = packets.values()
	packets_sorted.sort(key=lambda p: p['tx']['data'])

	return packets_sorted

def process_campaign_2():

	packets_sorted = load_pkts("raw/tx_log", "raw/rx_log")

	#print packets

	packets_1 = []
	packets_2 = []
	packets_3 = []

	for p in packets_sorted:
		# in this campaign, a static "multiply by const" GNU radio was
		# used to set gain.
		assert 'gain' not in p['tx']
		p['tx']['gain'] = 20. * log10(.6)

		if 'frequency' in p['tx']:
			packets_3.append(p)
		elif 'repetitions' in p['tx']:
			packets_2.append(p)
		else:
			packets_1.append(p)

	f = open(OUTPATH + '/sfxlib.json', 'w')
	json.dump(packets_1, f, indent=4)
	f.close()

	f = open(OUTPATH + '/sfxlib_norep.json', 'w')
	json.dump(packets_2, f, indent=4)
	f.close()

	f = open(OUTPATH + '/sfxlib_norep_randfreq.json', 'w')
	json.dump(packets_3, f, indent=4)
	f.close()

def process_campaign_3():
	pkts = load_pkts("raw/tx2_log", "raw/rx2_log")

	f = open(OUTPATH + '/sfxlib_norep_randfreq2.json', 'w')
	json.dump(pkts, f, indent=4)
	f.close()

def process_campaign_5():
	pkts = load_pkts("raw/tx5_log", "raw/rx5_log")

	f = open(OUTPATH + '/sfxlib_norep_randfreq_randgain.json', 'w')
	json.dump(pkts, f, indent=4)
	f.close()

def process_campaign_6():
	pkts = load_pkts("raw/tx6_log", "raw/rx6_log")

	for pkt in pkts:
		pkt['tx']['attenuator'] = -30.

	f = open(OUTPATH + '/sfxlib_norep_randfreq_randgain_30att.json', 'w')
	json.dump(pkts, f, indent=4)
	f.close()

def main():
	process_campaign_2()
	#process_campaign_3()
	process_campaign_5()
	process_campaign_6()

main()
