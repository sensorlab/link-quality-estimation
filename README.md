## Link quality estimation

Code samples and datasets that are related to link quality estimation.

### Directory structure

<dl>
  <dt>datasets</dt>
  <dd>Datasets (and their corresponding Python scripts) that are related to link quality estimation.</dd>

  <dt>featureGenerator</dt>
  <dd>Feature generator is a Python script used for extraction and computation of new features from generic data. Output of this script is labelled data in <em>Attribute-Relation File Format</em> (ARFF), which can be further used for data modelling.</dd>

  <dt>wekaClassificationModelBuilder</dt>
  <dd>Weka classification model builder (WCMB) is a Java program based on Weka (Waikato Environment for Knowledge Analysis). WCMB is used for building custom classification models in bulk by utilizing all possible combinations of input features.</dd>

  <dt>wmewmaEstimator</dt>
  <dd>Window mean with exponentially weighted moving average (WMEWMA) link quality estimator proposed by A. Woo <em>et al.</em> in paper <em>Taming the Underlying Challenges of Reliable Multihop Routing in Sensor Networks</em> implemented as a simple Python script.</dd>
</dl>

### Conventional work flow

1. Transform a dataset to a common format used by the feature generator (use dataset-specific scripts).
2. Use *featureGenerator* to generate features and transform the dataset to the common format used by Weka.
3. Build models with *wekaClassificationModelBuilder*.

### Citation
If you are using our datasets or scripts in your research, citation of the following paper would be greatly appreciated.

[Kulin, M., Fortuna, C., De Poorter, E., Deschrijver, D., & Moerman, I. (2016). Data-Driven Design of Intelligent Wireless Networks: An Overview and Tutorial. Sensors, 16(6), 790.](http://www.mdpi.com/1424-8220/16/6/790/htm)

### License

See `README.md` files in individual sub-directories for details.

### Acknowledgement

The research leading to these results has received funding from the European Horizon 2020 Programme project eWINE under grant agreement No. 688116.