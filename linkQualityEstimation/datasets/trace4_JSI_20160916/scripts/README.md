# Scripts [trace4_JSI_20160916]

Scripts for data transformation and generation of data statistics.

## Prerequisites

All scripts require Python 2.7, some scripts also require the following Python packages:

* natsort (*statistics.py*, *transform.py*)
* Matplotlib (*correlation_graphs.py*, *generate_data_weka_clustering.py*, *graph_rssi_time.py*)
* sklearn (*statistics.py*)
* pandas (*statistics.py*)

One way of installing Python 2.7:

```shell
sudo apt-get install python
```

One may install the Python packages in the following manner:

1. Install pip: `sudo apt-get install python-pip`
2. Install the packages: `pip install natsort matplotlib sklearn pandas`

## Usage

All scripts can be run in the following way:

```shell
python name_of_the_script.py
```

where *name_of_the_script.py* is the name of the script we want to execute.

## Description

Descriptions of all scripts in this directory.

#### correlation_graphs.py

This script illustrates the correlation between SNR and transmission gain. Complete range of transmission gain is split into an arbitrary number of bins, then each bin is filled with their corresponding measurements.

#### generate_data_weka_clustering.py

This script calculates average RSSI per window and corresponding PRR then outputs the data to an [ARFF](http://www.cs.waikato.ac.nz/ml/weka/arff.html) file (which may be used by [Weka](http://www.cs.waikato.ac.nz/ml/weka/index.html)). This data can be used for clustering. The script also plots windowed average RSSI vs PRR.

#### graph_rssi_time.py

This script illustrates RSSI values for all (received) packets per each link. Packets are in chronological order.

#### statistics.py

This script calculates a five number summary of RSSI values for each link. To use this script, data must first be transformed using *transform.py*.

#### transform.py

This script transforms the data to a common format used by the Feature generator. The data is output to the Feature generator's *datasets* directory. The script does not handle missing values (packets) by using interpolation.