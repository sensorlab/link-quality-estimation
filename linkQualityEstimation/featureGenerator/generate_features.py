'''
TODO:
- sanitize and check input (datasets/experiments)
- make selection of arguments (datasets etc.) available through command line

'''
import os
from natsort import natsorted

DATASET_PATH = "./datasets/"

# returns all available datasets and corresponding experiments
def get_all_datasets_experiments(dataset_path = DATASET_PATH):
	return

# selects dataset and corresponding experiments from user input
def select_datasets_experiments(dataset_path = DATASET_PATH):
	selected_datasets = []
	selected_experiments = []
	return selected_datasets, selected_experiments

# imports the selected datasets and corresponding experiments
def import_datasets_experiments(selected_datasets, selected_experiments, dataset_path = DATASET_PATH):
	select_datasets_experiments(dataset_path)

	return

if __name__ == "__main__":
	# select the input data, i.e. the datasets and experiments, and import it
	datasets, experiments = select_datasets_experiments()
	import_datasets_experiments(datasets, experiments)
