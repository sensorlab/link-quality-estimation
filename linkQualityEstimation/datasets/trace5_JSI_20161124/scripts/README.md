# Scripts [trace5_JSI_20161124]

Scripts for data transformation and generation of data statistics.

## Prerequisites

All scripts require Python 2.7, some scripts also require the following Python packages:

* NumPy (*statistics.py*, *transform.py*)
* natsort (*transform.py*)
* Matplotlib (*statistics.py*)
* pandas (*statistics.py*, *transform.py*)
* sklearn (*statistics.py*)
* SciPy (*statistics.py*)

One way of installing Python 2.7:

```shell
sudo apt-get install python
```

One may install the Python packages in the following manner:

1. Install pip: `sudo apt-get install python-pip`
2. Install the packages: `pip install numpy natsort matplotlib pandas sklearn scipy`

## Usage

All scripts can be run in the following way:

```shell
python name_of_the_script.py
```

where *name_of_the_script.py* is the name of the script we want to execute.

## Description

Descriptions of all scripts in this directory.

#### statistics.py

This script calculates PRR and a five number summary of RSSI values for each link. The script also illustrates PRR vs transmission gain, RSSI vs transmission gain and RSSI vs PRR.

#### transform.py

This script transforms the data to a common format used by the Feature generator. We use interpolation to calculate missing values for lost packets. The data is output to the Feature generator's *datasets* directory.