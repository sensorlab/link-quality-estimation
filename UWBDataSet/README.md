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

	+ code
		|____ uwb_dataset.py
	+ dataset
		|____ uwb_dataset_part1.csv
		|____ uwb_dataset_part2.csv
		|____ uwb_dataset_part3.csv
		|____ uwb_dataset_part4.csv
		|____ uwb_dataset_part5.csv
		|____ uwb_dataset_part6.csv
		|____ uwb_dataset_part7.csv

Whole data set is randomized and later split into 7 smaller files.

## File Structure
First line in every data set file is a header with column names. Elements of every sample are:
* NLOS (1 if NLOS, 0 if LOS)
* Measured range (time of flight)
* FP_IDX (index of detected first path element in CIR accumulator: in data set it can be accessed by **first_path_index+15**)
* FP_AMP1 (first path amplitude - part1) [look in user manual](http://thetoolchain.com/mirror/dw1000/dw1000_user_manual_v2.05.pdf)
* FP_AMP2 (first path amplitude - part2) [look in user manual](http://thetoolchain.com/mirror/dw1000/dw1000_user_manual_v2.05.pdf) 
* FP_AMP3 (first path amplitude - part3) [look in user manual](http://thetoolchain.com/mirror/dw1000/dw1000_user_manual_v2.05.pdf)
* STDEV_NOISE (standard deviation of noise)
* CIR_PWR (total channel impulse response power)
* MAX_NOISE (maximum value of noise)
* RXPACC (received RX preamble symbols)
* CH (channel number)
* FRAME_LEN (length of frame)
* PREAM_LEN (preamble length)
* BITRATE
* PRFR (pulse repetition frequency rate in MHz)
* CIR (absolute value of channel impulse response: 1016 samples with 1 nanosecond resolution)

## Importing Data Set in Python
To import data set data into Python environment, **uwb_dataset.py** script from folder **code** can be used. 
