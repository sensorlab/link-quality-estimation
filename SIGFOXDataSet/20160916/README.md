# SIGFOX 20160916 packet dataset

This dataset contains results of some tests with sending SIGFOX frames from a
device to basestation.

In all tests, basestation was mounted on the roof of JSI building C. Device was
in office N403 (building N). I.e. non-line of sight, link was indoor to
outdoor.

Transmitter was USRP N200, SBX daughterboard. Front-end PA gain was set to 0
dB. VERT900 antenna was used in a vertical position. Some measurements were
made with mini-circuits 30 dB attenuator connected between the USRP and the
antenna. Baseband data before attenuation had full DAC range -1 to +1.

MAC layer was as implemented in libIJS_SIGFOX_LIB_V1.8.7.a.

File format is JSON. Each file contains a list of objects. Each object
describes one packet:

    {
        "rx": {
            "seqNumber": "2328",
            "avgSnr": "8.91",
            "station": "0BF2",
            "snr": "8.25",
            "time": "1473760937",
            "device": "1CF14C",
            "rssi": "-79.00",
            "data": "0000"
        },
        "tx": {
            "attenuator": 0.0,
            "frequency": 868165999.872908,
            "repetitions": 1,
            "data": "0000",
            "gain": -7.632667198777199
        }
    },

"tx" property contains values related to the transmission of the packet.  Where
"frequency" and/or "repetitions" is missing, they were left to be defined by
SIGFOX_LIB.

"gain" is the baseband gain in decibels. Gain was set by multiplying packet
baseband data (i.e. in the digital domain, NOT by setting USRP PA gain).

"attenuator" is the external attenuator gain. 0 if attenuator was not used.

"rx" property contains data returned by the basestation upon reception of the
packet. If "rx" property is absent, the packet was not received by the
basestation.

In all cases, packet payload ("data" property) was used to transmit a sequence
number. This sequence number was used to connect the log of transmitted packets
with basestation reports.


## Description of individual files:

 *  `sfxlib.json`

	1000 packets sent using the original protocol defined by SIGFOX_LIB (3
	repetitions, some proprietary frequency hopping pattern)

 *  `sfxlib_norep.json`

	1000 packets using the original protocol defined by SIGFOX_LIB, except
	only the first packet repetition was transmitted.

 *  `sfxlib_norep_randfreq.json`

	1000 packets using one repetition on a randomly chosen frequency (i.e.
	overriding the hopping pattern defined by SIGFOX_LIB)

 *  `sfxlib_norep_randfreq_randgain.json`

	5000 packets using one repetition, randomly chosen frequency and
	randomly chosen baseband gain between -30 and 0 dB.

 *  `sfxlib_norep_randfreq_randgain_30att.json`

	5000 packets using one repetition, randomly chosen frequency and
	randomly chosen baseband gain between -30 and 0 dB. 30 dB external
	attenuator between USRP and antenna to further decrease transmit power.


The "scripts/" sub-directory contains code that was used to obtain these measurements:

 *  `sigfox_loop.json`

	Transmit-receive loop for logging raw packet data, implemented as a
	node RED flow.

	Note that running this flow requires external software components that
	are not included in this repository.

 *  `process.py`

	Post-processing script that was used to transform raw data into JSON
	files included in this dataset.

## Contact

For any additional information please contact **tomaz.solc@ijs.si**

## License

Copyright (C) 2017 SensorLab, Jožef Stefan Institute http://sensorlab.ijs.si

The research leading to these results has received funding from the European
Horizon 2020 Programme project eWINE under grant agreement No. 688116.

Data is available under the Creative Commons Attribution 4.0 International
(CC BY 4.0) license.
