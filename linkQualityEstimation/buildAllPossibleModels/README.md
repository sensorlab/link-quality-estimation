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

```
sudo apt-get install openjdk-7-jdk openjdk-7-jre
```

To obtain Weka, download it from [the official website](http://www.cs.waikato.ac.nz/ml/weka/downloading.html). Next, extract the downloaded archive file and copy *weka.jar* into the `wekaClassificationModelBuilder/code/` directory.

### Usage

WekaModellalal must first be instantiated.

### Building/running an example

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
javac -cp ".:weka.jar" WekaClassificationModelBuilder.java WekaClassificationModelBuilderExample.java
```

And repeat

```
java -cp ".:weka.jar" WekaClassificationModelBuilderExample
```

End with an example of getting some data out of the system or using it for a little demo