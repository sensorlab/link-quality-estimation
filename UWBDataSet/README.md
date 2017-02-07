# UWB LOS and NLOS Data Set
Data set was created using [SNPN-UWB](http://www.log-a-tec.eu/mtc.html) board with DecaWave [DWM1000](http://www.decawave.com/sites/default/files/resources/dwm1000-datasheet-v1.3.pdf) UWB radio module. 

## Data Set Description
Measurements were taken on 7 different indoor locations:
* Office1
* Office2
* Small appartment
* Small workshop
* Kitchen with a living room
* Bedroom
* Boiler room.
42000 samples were taken: 21000 for LOS and 21000 for NLOS channel condition.
For measurements two UWB nodes were used: one node as an anchor and the second node as a tag. Only traces of LOS and NLOS channel measurements were taken without any reference positioning (this data set is not appropriate for localization evaluation).

## Data Set Structure
Folder with data set is organized as follows:

	+ **code**
		|____ uwb_dataset.py
	+ **dataset**
		|____ uwb_dataset_part1.csv
		|____ uwb_dataset_part2.csv
		|____ uwb_dataset_part3.csv
		|____ uwb_dataset_part4.csv
		|____ uwb_dataset_part5.csv
		|____ uwb_dataset_part6.csv
		|____ uwb_dataset_part7.csv

