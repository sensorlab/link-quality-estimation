# Weka classification model builder

Weka classification model builder (WCMB) is a Java program based on Weka (Waikato Environment for Knowledge Analysis). WCMB is used for building custom classification models in bulk by utilizing all possible combinations of input features.

## Components

WCMB consists of the following components:

* **WekaClassificationModelBuilder.java** - Contains the main class.
* **WekaClassificationModelBuilderExample.java** - A sample usage.

## Getting Started

These instructions will get you a copy of the WCMB up and running on your local machine for development and testing purposes. The rest of this section assumes a Linux (namely Linux Mint) machine is being used.

### Prerequisites

WCMB requires Weka libraries and Java. One way of installing Java:

```shell
sudo apt-get install openjdk-7-jdk openjdk-7-jre
```

To obtain Weka, download it from [the official website](http://www.cs.waikato.ac.nz/ml/weka/downloading.html). Next, extract the downloaded archive file and copy *weka.jar* into the *wekaClassificationModelBuilder/code/* directory.

### Usage

WCMB must first be instantiated:

```java
WekaClassificationModelBuilder wmb = new WekaClassificationModelBuilder(FILE, OUT, UNWANTEDATTR);
```

where **FILE** is a (string) path to the input *.arff* file, **OUT** is a (string) path to output directory and **UNWANTEDATTR** is an array of unwanted attributes (strings) that must first be removed before building the models. Next, we build all possible models:


```java
wmb.buildAllModels(OUTTOFILE, CLS, FOLDS);
```

where **OUTTOFILE** is a boolean value describing whether to output every single model to a file, **CLS** is a [Classifier](http://weka.sourceforge.net/doc.dev/weka/classifiers/Classifier.html) and **FOLDS** is a (integer) number of folds used for cross-validation.

For a complete example, see *WekaClassificationModelBuilderExample.java*.

### Building/running an example

To run the example, we must first build all Java files. We do so by running the following command:

```shell
javac -cp ".:weka.jar" WekaClassificationModelBuilder.java WekaClassificationModelBuilderExample.java
```

We run the example:

```shell
java -cp ".:weka.jar" WekaClassificationModelBuilderExample
```

Sample console output:
```
Used attrs: snr rssi_std rssi_avg avgSnr 
Top of the tree: rssi_avg
Used attrs: timestamp snr rssi_std rssi_avg avgSnr 
Top of the tree: rssi_avg
Used attrs: snr_avg rssi_std rssi avgSnr 
Top of the tree: snr_avg
Used attrs: snr_avg snr rssi_std rssi_avg rssi 
Top of the tree: rssi_avg
Used attrs: timestamp snr_avg snr rssi_std rssi_avg rssi 
Top of the tree: rssi_avg
...
```

## Author and license

Weka classification model builder was written by Timotej Gale, **timotej.gale@gmail.com**.

Copyright (C) 2017 SensorLab, Jožef Stefan Institute http://sensorlab.ijs.si

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses

## Acknowledgement

The research leading to these results has received funding from the European Horizon 2020 Programme project eWINE under grant agreement No. 688116.