# Scripts [trace1_Rutgers]

Scripts for data transformation and generation of data statistics.

## Prerequisites

All scripts require Python 2.7, some scripts also require the following Python packages:

* natsort (*transform.py*)
* Matplotlib (*per_link.py*, *per_link_windows.py*, *per_transmitter.py*, *prepare_data_clustering.py*)
* pandas (*per_link.py*, *per_transmitter.py*, *transform.py*)
* NumPy (*prepare_data_clustering.py*, *transform.py*)

One way of installing Python 2.7:

```shell
sudo apt-get install python
```

One may install the Python packages in the following manner:

1. Install pip: `sudo apt-get install python-pip`
2. Install the packages: `pip install natsort matplotlib pandas numpy`

## Usage

All scripts can be run in the following way:

```shell
python name_of_the_script.py
```

where *name_of_the_script.py* is the name of the script we want to execute.

## Description

Descriptions of all scripts in this directory.


#### per_link.py

This script does the following for each link: Plots RSSI in relation to time, plots a histogram of RSSI, and calculates a five number summary of RSSI, then outputs everything to the *output* directory. The script also plots average RSSI versus PRR of each link.

#### per_link_windows.py

This script calculates PRR and average RSSI across all data divided into windows of specified size. The results are plotted.

#### per_transmitter.py

This script plots a histogram of RSSI and calculates a five number summary of RSSI for all packets of each transmitter. The results are output to the *output* directory.

#### prepare_data_clustering.py

This script calculates average RSSI and corresponding PRR per link, then groups the links by noise level and outputs the data to [ARFF](http://www.cs.waikato.ac.nz/ml/weka/arff.html) files (which may be used by [Weka](http://www.cs.waikato.ac.nz/ml/weka/index.html) for clustering) to the *output* directory. The resulting data also includes RSSI distribution information.

#### transform.py

This script transforms the data to a common format used by the Feature generator. We use interpolation to calculate missing values for lost packets. The data is output to the Feature generator's *datasets* directory.