## Link quality estimation

Code samples and datasets that are related to link quality estimation.

### Directory structure

<dl>
  <dt>datasets</dt>
  <dd>Datasets (and their corresponding Python scripts) that are related to link quality estimation.</dd>

  <dt>notebooks</dt>
  <dd>Jupyter notebooks that are related to the datasets analysis and/or link quality estimation.</dd>
</dl>

### Conventional work flow
1. Install python dependencies
2. Run desired scripts directly (e.g. `python ./datasets/trace1_Rutgers/transform.py`)
3. Perform analysis on preprocessed dataset:
    - Use your own tools on CSV files, which were produced in *./output/datasets/<dataset_name>/*
    - or use this project as python package and adapt it to your needs. (e.g. `from datasets.trace1_Rutgers import get_traces`)

### Citation

If you are using our datasets or scripts in your research, citation of any of the following papers would be greatly appreciated.

[Cerar, G., Yetgin, H., Mohorčič, M., Fortuna, C. (2021). Machine Learning for Link Quality Estimation: A Survey](https://doi.org/10.1109/COMST.2021.3053615)

[Kulin, M., Fortuna, C., De Poorter, E., Deschrijver, D., & Moerman, I. (2016). Data-Driven Design of Intelligent Wireless Networks: An Overview and Tutorial. Sensors, 16(6), 790.](http://www.mdpi.com/1424-8220/16/6/790/htm)

### Work in progress

This repository is gradually migrating toward Python 3.4+ and package oriented approach. *Trace1_Rutgers* is currently up to date, while unfortunately other datasets may require Python 2 with obsolete packages for preprocessing. We are sorry for inconvenience.

### License

See `README.md` files in individual sub-directories for details.

### Acknowledgement

The research leading to these results has received funding from the European Horizon 2020 Programme projects NRG-5 under grant agreement No. 762013 and eWINE under grant agreement No. 688116.
