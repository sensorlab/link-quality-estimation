## Dataset - Jožef Stefan Institute (24 November 2016)

**This dataset contains results of some tests with sending SIGFOX frames from a device to basestation.**

Basestation was mounted on the roof of JSI building C. Device was moved on a trolley through 4 different in-door locations (so link was always indoor to outdoor).

Following locations were used:

    0 - Office N403
    1 - E6 hall by the water cooler
    2 - Main hall in front of the big lecture room
    3 - Sensor lab

Transmitter was USRP N200, SBX daughterboard. Front-end PA gain was varied from 0 dB to 30 dB in steps of 10 dB. VERT900 antenna was used in a vertical position. Baseband data had full DAC range -1 to +1. A 30 dB attenuator was installed between the USRP output and the antenna.

At each location, 100 packets were sent for each of the 4 gain settings.

MAC layer was as implemented in libIJS_SIGFOX_LIB_V1.8.7.a.

In this dataset, the frequency of packet transmission was left to be defined by SIGFOX_LIB, however only the first of three normal packet repetitions was actually transmitted.

## Dataset description

Full dataset description can be found in *data* directory.
### Directory structure

<dl>
  <dt>data</dt>
  <dd>The actual data.</dd>

  <dt>scripts</dt>
  <dd>Scripts for data transformation and generation of data statistics.</dd>
</dl>