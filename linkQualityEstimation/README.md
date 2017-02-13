## Link quality estimation

Code samples and datasets that are related to WP5 and localization.

### Directory structure

<dl>
  <dt>**datasets**</dt>
  <dd>TODO</dd>

  <dt>**featureGenerator**</dt>
  <dd>TODO</dd>

  <dt>**wekaClassificationModelBuilder**</dt>
  <dd>TODO</dd>

  <dt>**wmewmaEstimator**</dt>
  <dd>TODO</dd>
</dl>

### Conventional work flow

1. Transform dataset to a common format used by the feature generator (use dataset-specific scripts).
2. Use *featureGenerator* to generate features and transform the dataset to a common format used by Weka.
3. Build models with *wekaClassificationModelBuilder*.