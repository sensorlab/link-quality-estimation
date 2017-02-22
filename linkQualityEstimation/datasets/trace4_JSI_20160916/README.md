# Dataset - Jožef Stefan Institute (16 September 2016)

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

## Author and license

Scripts for this dataset were written by Timotej Gale, **timotej.gale@gmail.com**.

Copyright (C) 2017 SensorLab, Jožef Stefan Institute http://sensorlab.ijs.si

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses

## Acknowledgement

The research leading to these results has received funding from the European Horizon 2020 Programme project eWINE under grant agreement No. 688116.