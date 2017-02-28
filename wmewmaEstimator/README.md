# WMEWMA link quality estimator

Window mean with exponentially weighted moving average (WMEWMA) link quality estimator proposed by A. Woo *et al.* in paper *Taming the Underlying Challenges of Reliable Multihop Routing in Sensor Networks* implemented as a simple Python script.

## Components

Different types of WMEWMA link quality estimator are implemented in the following fashion:

* **wmewma_real_time.py** - Simulation of WMEWMA estimator in real time.
* **wmewma_static.py** - WMEWMA estimator that works on static data (e.g. data files).
* **wmewma_trace1_py** - Parallel real time simulation of WMEWMA estimator on Rutgers dataset (trace 1).

## Getting Started

These instructions will get you a copy of the WMEWMA link quality estimator up and running on your local machine for development and testing purposes. The rest of this section assumes a Linux (namely Linux Mint) machine is being used.

### Prerequisites

WMEWMA link quality estimator requires Pyton 2.7. One way of installing Python 2.7:

```shell
sudo apt-get install python
```

### Real-time WMEWMA

Simulation of WMEWMA estimator in real time.

#### Configuration

Real-time WMEWMA can have the following parameters altered (in the script):

* **ALPHA** - Controls the history of the estimator, range [0, 1].
* **MIN_DATA_FREQUENCY** - Minimum message rate, one packet per x miliseconds, e.g. 10000 (1 packet / 10 seconds).
* **ESTIMATE_TO_DATA_RATIO** - Defines time window, e.g. 20 means estimation is performed every 20 times MIN_DATA_FREQUENCY.

#### Usage

Running the script:

```shell
python wmewma_real_time.py
```

The script will now read packets' sequence numbers from standard input and calculate the estimations. We can connect the input of WMEWMA estimator to output of some other command via a *pipeline*.

---

### Static WMEWMA

WMEWMA estimator that works on static data (e.g. data files).

#### Configuration

Static WMEWMA can have the following parameters altered (in the script):

* **ALPHA** - Controls the history of the estimator, range [0, 1].
* **PACKETS_PER_WINDOW** - A number of lines to read from a file at once.
* **FILE** - Input file with data.

##### Input file format

Each row of the input file must have two values separated by a blank space: a sequence number and a measurement, e.g.:

```
0 -55
1 -55
3 -56
5 -55
```

#### Usage

Running the script:

```shell
python wmewma_static.py
```

The script will now read packets' sequence numbers from the specified file and calculate the estimations.

---

### Trace 1 WMEWMA

Parallel real time simulation of WMEWMA estimator on Rutgers dataset (trace 1).

#### Configuration

Trace 1 WMEWMA can have the following parameters altered (in the script):

* **ALPHA** - Controls the history of the estimator, range [0, 1].
* **MIN_DATA_FREQUENCY** - Minimum message rate, one packet per x miliseconds, e.g. 10000 (1 packet / 10 seconds).
* **ESTIMATE_TO_DATA_RATIO** - Defines time window, e.g. 20 means estimation is performed every 20 times MIN_DATA_FREQUENCY.
* **SLEEP** - Time in *seconds* between packet "transmissions".

#### Usage

Running the script:

```shell
python wmewma_trace1.py
```

The script will now simulate real time transmission of packets to the estimator, calculate the estimations and output the estimations to a file. We can run multiple instances of this script simultaneously.

## Author and license

WMEWMA link quality estimator scripts were written by Timotej Gale, **timotej.gale@gmail.com**.

Copyright (C) 2017 SensorLab, Jožef Stefan Institute http://sensorlab.ijs.si

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses

## Acknowledgement

The research leading to these results has received funding from the European Horizon 2020 Programme project eWINE under grant agreement No. 688116.