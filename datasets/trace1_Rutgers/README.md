# Dataset - Rutgers University

**Traceset of RSSI measurement from the ORBIT testbed.**

This traceset includes received signal strength indication (RSSI) for each correctly received frame at receiving nodes when various levels of noise are injected into the ORBIT testbed.

## Dataset description

Full dataset description can be found [here](https://crawdad.cs.dartmouth.edu/rutgers/noise/20070420/).

### Directory structure

<dl>
  <dt><strong>data/</strong></dt>
  <dd>The actual data.</dd>

  <dt><strong>transform.py</strong></dt>
  <dd>
    Transforms traces from <i>data/</i> directory into flat structured, where missing sequence numbers are added, but no interpolation is performed. The output files reside in <i>${PROJECT_ROOT}/output/datasets/dataset-2-rutgers-wifi/</i> in a comma-separated values (CSV) format. All CSV files contain these seven columns with respective data types:
    <ul>
      <li>seq (sequence number) as <i>uint16</i> type</li>
      <li>src (source/transmitter node) as <i>string</i> type</li>
      <li>dst (destination/receiver node) as <i>string</i> type</li>
      <li>noise (artificial noise level) as <i>int8</i> type</li>
      <li>received (packet reception) as <i>boolean</i> type</li>
      <li>error (error indicator, RSSI == 128) as <i>boolean</i> type</li>
      <li>rssi (Reception Signal Strength Indicator) as <i>uint8</i> type</li>
    </ul>
  </dd>
  <dt><strong>interpolation.py</strong></dt>
  <dd>
    By default, `transform.py` preserve information regarding lost packets and missing RSSI values are filled with zeros. This script provides other interpolation methods on each trace CSV file in <i>${PROJECT_ROOT}/featureGenerator/datasets/dataset-2-rutgers-wifi/</i> on <strong>rssi</strong> column. Run script with `-h` or `--help` parameter for further instructions.
  </dd>
</dl>

## Usage

0. use either **virtualenv** or **conda** environment prior next steps. **(recommended)**
1. from root of this project run: `pip install -e .` or `conda develop .`
2. Run specific script e.g. `python ./transform.py`


## Author and license

Scripts for this dataset were written by Gregor Cerar. Contact me via email firstname.lastname@ijs.si pattern.

Copyright (C) 2019 SensorLab, Jožef Stefan Institute http://sensorlab.ijs.si

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses

## Acknowledgement

The research leading to these results has received funding from the European Horizon 2020 Programme project eWINE under grant agreement No. 688116.
