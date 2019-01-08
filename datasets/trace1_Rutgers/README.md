# Dataset - Rutgers University

**Traceset of RSSI measurement from the ORBIT testbed.**

This traceset includes received signal strength indication (RSSI) for each correctly received frame at receiving nodes when various levels of noise are injected into the ORBIT testbed.

## Dataset description

Full dataset description can be found [here](https://crawdad.cs.dartmouth.edu/rutgers/noise/20070420/).

### Directory structure

<dl>
  <dt>data</dt>
  <dd>The actual data.</dd>

  <dt>scripts</dt>
  <dd>
    Scripts for data transformation and generation of data statistics.
    <dl>
      <dt><strong>transform.py</strong></dt>
      <dd>
        Transforms traces from <i>data/</i> directory into flat structured, where missing sequence numbers are added, but no interpolation is performed. The output files reside in <i>${PROJECT_ROOT}/featureGenerator/datasets/dataset-2-rutgers-wifi/</i> in a comma-separated values (CSV) format. All CSV files contain these six columns with respective data types:
        <ul>
          <li>seq (sequence number) as <i>uint16</i> type</li>
          <li>src (source/transmitter node) as <i>string</i> type</li>
          <li>dst (destination/receiver node) as <i>string</i> type</li>
          <li>noise (artificial noise level) as <i>int8</i> type</li>
          <li>received (packet reception) as <i>boolean</i> type</li>
          <li>rssi (Reception Signal Strength Indicator) as <i>float32</i> type</li>
        </ul>
      </dd>
      <dt><strong>interpolation.py</strong></dt>
      <dd>
        It applies desired interpolation onto each CSV file in <i>${PROJECT_ROOT}/featureGenerator/datasets/dataset-2-rutgers-wifi/</i> on <strong>rssi</strong> column. Run script with `-h` or `--help` parameter for further instructions.
      </dd>
      <dt>
        <strong>
          per_link_windows.py<br/>
          per_link.py<br/>
          per_transmitter.py<br/>
          prepare_data_clustering.py
        </strong>
      </dt>
      <dd>These scripts visualize the dataset for visualization of the data.</dd>
      </dl>
  </dd>
</dl>

## Author and license

Scripts for this dataset were written by Adnan Bekan (**adnan.bekan@ijs.si**), Timotej Gale (**timotej.gale@gmail.com**) and Gregor Cerar.

Copyright (C) 2018 SensorLab, Jožef Stefan Institute http://sensorlab.ijs.si

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses

## Acknowledgement

The research leading to these results has received funding from the European Horizon 2020 Programme project eWINE under grant agreement No. 688116.
