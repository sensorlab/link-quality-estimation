SIGFOX 20161124 packet dataset
==============================

This dataset contains results of some tests with sending SIGFOX frames from a
device to basestation.

Basestation was mounted on the roof of JSI building C. Device was moved on a
trolley through 4 different in-door locations (so link was always indoor to
outdoor).

Following locations were used:

    0 - Office N403
    1 - E6 hall by the water cooler
    2 - Main hall in front of the big lecture room
    3 - Sensor lab

Transmitter was USRP N200, SBX daughterboard. Front-end PA gain was varied from
0 dB to 30 dB in steps of 10 dB. VERT900 antenna was used in a vertical
position. Baseband data had full DAC range -1 to +1. A 30 dB attenuator was
installed between the USRP output and the antenna.

At each location, 100 packets were sent for each of the 4 gain settings.

MAC layer was as implemented in libIJS_SIGFOX_LIB_V1.8.7.a.

In this dataset, the frequency of packet transmission was left to be defined by
SIGFOX_LIB, however only the first of three normal packet repetitions was
actually transmitted.

File format
-----------

File format is JSON. Top level object contains one property:

    {
        "campaigns": [
            ...
        ],
    }

For each location, one measurement campaign was conducted. For each campaign
there is an object with the following properties:

    {
        "location": ...
        "packets": ...
    }

"location" property contains location number (see list and map above).

"packets" property contains a list of "packet" objects. Each "packet" object
describes one transmitted packet:

    {
        "rx": {
            "seqNumber": "2461",
            "avgSnr": "10.67",
            "station": "0BF2",
            "snr": "8.73",
            "time": "1477563622",
            "device": "1CF14C",
            "rssi": "-109.00",
            "data": "0000"
        },
        "tx": {
            "attenuator": -30.0,
            "timestamp": 1477564048.682,
            "repetitions": 1,
            "pga_gain": 0,
            "frequency": [
                868194200
            ],
            "data": "0000"
        }
    }

"tx" property contains values related to the transmission of the packet.
"repetitions" is the number of times the packet was transmitted. "frequency" is
the carrier frequency (in hertz).

"pga_gain" property contains the front-end power amplifier gain (in decibells).

"rx" property contains data returned by the basestation upon reception of the
packet. If "rx" property is absent, the packet was not received by the
basestation.

Packet payload ("data "property) was used to transmit a sequence
number. This sequence number was used to connect the log of transmitted packets
with basestation reports.

## Contact

For any additional information please contact **tomaz.solc@ijs.si**

## License

Copyright (C) 2017 SensorLab, Jožef Stefan Institute http://sensorlab.ijs.si

The research leading to these results has received funding from the European
Horizon 2020 Programme project eWINE under grant agreement No. 688116.

Data is available under the Creative Commons Attribution 4.0 International
(CC BY 4.0) license.
