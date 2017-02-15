## Dataset - Jožef Stefan Institute (16 September 2016)

**This dataset contains results of some tests with sending SIGFOX frames from a device to basestation.**

In all tests, basestation was mounted on the roof of JSI building C. Device was in office N403 (building N). I.e. non-line of sight, link was indoor to outdoor.

Transmitter was USRP N200, SBX daughterboard. Front-end PA gain was set to 0 dB. VERT900 antenna was used in a vertical position. Some measurements were made with mini-circuits 30 dB attenuator connected between the USRP and the antenna. Baseband data before attenuation had full DAC range -1 to +1.

MAC layer was as implemented in libIJS_SIGFOX_LIB_V1.8.7.a.

## Dataset description

[Full dataset description](../../../SIGFOXDataSet/20160916/README) can be found in *data* directory.
### Directory structure

<dl>
  <dt>data</dt>
  <dd>The actual data.</dd>

  <dt>scripts</dt>
  <dd>Scripts for data transformation and generation of data statistics.</dd>

  <dt>figures</dt>
  <dd>Complementary figures to the dataset description.</dd>
</dl>