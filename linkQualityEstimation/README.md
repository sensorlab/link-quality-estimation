## Link quality estimation

Code samples and datasets that are related to link quality estimation.

### Directory structure

<dl>
  <dt>datasets</dt>
  <dd>Datasets (and their corresponding Python scripts) that are related to link quality estimation.</dd>

  <dt>featureGenerator</dt>
  <dd>Feature generator is a Python script used for extraction and computation of new features from generic data. Output of this script is labelled data in *Attribute-Relation File Format* (ARFF), which can be further used for data modelling.</dd>

  <dt>wekaClassificationModelBuilder</dt>
  <dd>Weka classification model builder (WCMB) is a Java program based on Weka (Waikato Environment for Knowledge Analysis). WCMB is used for building custom classification models in bulk by utilizing all possible combinations of input features.</dd>

  <dt>wmewmaEstimator</dt>
  <dd>Window mean with exponentially weighted moving average (WMEWMA) link quality estimator proposed by A. Woo *et al.* in paper *Taming the Underlying Challenges of Reliable Multihop Routing in Sensor Networks* implemented as a simple Python script.</dd>
</dl>

### Conventional work flow

1. Transform dataset to a common format used by the feature generator (use dataset-specific scripts).
2. Use *featureGenerator* to generate features and transform the dataset to the common format used by Weka.
3. Build models with *wekaClassificationModelBuilder*.