'''
TODO:
- sanitize and check input (datasets/experiments, ...)
- make selection of arguments (datasets etc.) available through command line parameters
- figure out what other features to add
- dynamically update available features
- human friendly warnings
- numpy array types
- when computing PRR, include the current received packet?
- put feature enrichment for loops (dataset/experiment/link) in a function that returns an iterable, also category definition - unified way of accessing
- avoid repetitive casting, calculating the same number N times in loops
- WARNINGS, ERROR CHECKING
- correct (more appropriate) data type in output file, input
- support for exporting string features
- dataset/experiment numbers in output file should match the input file numbers
'''

import os, shutil
from natsort import natsorted
import numpy as np
from collections import defaultdict
from numpy.lib.recfunctions import append_fields

DATASET_PATH = "./datasets/"
OUT_PATH = "./output/"
all_datasets = None
all_experiments = None

# returns all available datasets and corresponding experiments
def get_all_datasets_experiments(dataset_path = DATASET_PATH):
    global all_datasets, all_experiments
    if all((all_datasets, all_experiments)):
        return all_datasets, all_experiments
    all_datasets = {name.split("-")[1]: name for name in natsorted(os.listdir(dataset_path)) if os.path.isdir(os.path.join(dataset_path, name))}
    
    all_experiments = {}
    for dataset_number, dataset_name in all_datasets.items():
        data_dir = os.path.join(dataset_path, dataset_name)
        all_experiments[dataset_number] = {name.split("-")[1]: name for name in natsorted(os.listdir(data_dir)) if os.path.isdir(os.path.join(data_dir, name))}
    return all_datasets, all_experiments

# selects dataset and corresponding experiments from user input
def select_datasets_experiments(dataset_path = DATASET_PATH):
    selected_datasets = set()
    selected_experiments = defaultdict(set)
    datasets, experiments = get_all_datasets_experiments(dataset_path)
    while True:
        print("Please input the number of a dataset to be imported. Available datasets:")
        for dataset_number, dataset_name in sorted(datasets.items()):
            dataset_description = dataset_name.split("-")[-1]
            print(dataset_number + " ... " + dataset_description)
        number_selected_dataset = raw_input()
        selected_datasets.add(number_selected_dataset)
        
        
        print("Please input the numbers of experiments to be imported separated by a comma. Input * to select all experiments. Available experiments:")
        for experiment_number, experiment_name in sorted(experiments[number_selected_dataset].items()):
            experiment_description = experiment_name.split("-")[-1]
            print(experiment_number + " ... " + experiment_description)
        input_experiments = raw_input()
        for input_experiment in input_experiments.split(","):
            selected_experiments[number_selected_dataset].add(input_experiment.strip())

        print("Import another dataset/experiment? (y/n)")
        if not raw_input().upper() == "Y":
            break
    return selected_datasets, selected_experiments

# imports the selected datasets and corresponding experiments
def import_datasets_experiments(selected_datasets, selected_experiments, dataset_path = DATASET_PATH):
    # each link is a numpy matrix
    # return a multidimensional array of tuples (array/data, name)
    imported_data = []
    datasets, experiments = get_all_datasets_experiments(dataset_path)

    # replace asterisk with actual experiments
    for dataset in selected_datasets:
        for experiment in selected_experiments[dataset]:
            if experiment == "*":
                selected_experiments[dataset] = [exp.split("-")[1] for exp in experiments[dataset].values()]
                break
    
    for dataset in sorted(selected_datasets):
        dataset_name = datasets[dataset]
        imported_data.append(([], dataset_name))
        for experiment in sorted(selected_experiments[dataset]):
            experiment_name = experiments[dataset][experiment]
            imported_data[-1][0].append(([], experiment_name))
            links_path = os.path.join(dataset_path, datasets[dataset], experiments[dataset][experiment])
            for root, _, files in os.walk(links_path):
                for file in files:
                    link_data = np.genfromtxt(os.path.join(root, file), names=True, delimiter=',')
                    link_name = "".join(file.split(".")[:-1])
                    imported_data[-1][0][-1][0].append((link_data, link_name))
    print("Successfully imported.")
    return imported_data

# applies the specified transformation/enrichment wherever possible
# TODO: unified way of looping through all the data
def feature_enrichment(data, prr_window, avg_std, skip_leading):
    # prr
    if prr_window:
        no_seq = set()
        for dataset, dataset_name in data:
            for experiment, _ in dataset:
                for num_link, (link, link_name) in enumerate(experiment):
                    if "seq" not in link.dtype.names:
                        no_seq.add(dataset_name)
                        break
                    # calculate
                    prr_array = []
                    seq_numbers = link["seq"]
                    for curr_index, seq_number in enumerate(seq_numbers):
                        received = 0
                        backtrack = 0
                        # this also counts the current packet as received
                        # TODO: avoid calculating the same index two times
                        while curr_index - backtrack >= 0 and int(seq_number) - int(prr_window) < int(seq_numbers[curr_index - backtrack]):
                            backtrack += 1
                            received += 1
                        # add the difference for the first few packets
                        difference = int(seq_number) - int(prr_window) + 1
                        if difference < 0:
                            received += abs(difference)

                        prr = received / float(prr_window)
                        prr_array.append(prr)

                    experiment[num_link] = (append_fields(link, 'prr', prr_array), link_name)

        if no_seq:
            print("It was not possible to calculate PRR for the following datasets:", no_seq)
    
    # avg/std
    if avg_std:
        no_attr = set()
        no_attr_dataset = set()
        for transformation in avg_std.split(","):
            attribute, mode, window = transformation.strip().split(":")
            for dataset, dataset_name in data:
                for experiment, _ in dataset:
                    for num_link, (link, link_name) in enumerate(experiment):
                        if attribute not in link.dtype.names:
                            no_attr.add(attribute)
                            no_attr_dataset.add(dataset_name)
                            break
                        # calculate
                        results_array = []
                        attribute_values = link[attribute]
                        for curr_index in range(len(attribute_values)):
                            backtrack = 0
                            temp_values = []
                            # this also includes the current value in the result
                            # TODO: avoid calculating the same index three times
                            while curr_index - backtrack >= 0 and curr_index - backtrack > curr_index - int(window):
                                temp_values.append(float(attribute_values[curr_index - backtrack]))
                                backtrack += 1
                            if mode == "std":
                                if len(temp_values) <= 1:
                                    result = 0
                                else:
                                    result = np.std(temp_values, ddof=1) # corrected sample standard deviation
                            elif mode == "avg":
                                result = np.mean(temp_values)
                            else:
                                print("Unknown operation: " + mode)
                                quit() # TODO: handle exception
                            results_array.append(result)
                        experiment[num_link] = (append_fields(link, attribute + "_" + mode, results_array), link_name)

            if no_attr:
                print("It was not possible to calculate the following attributes on some datasets:", no_attr, no_attr_dataset)

    # truncate leading samples
    if skip_leading:
        for dataset, _ in data:
            for experiment, _ in dataset:
                for num_link, (link, link_name) in enumerate(experiment):
                    # TODO: input/error checking
                    experiment[num_link] = (np.delete(link, range(int(skip_leading)), axis=0), link_name)

    print("Transformations successfully applied.")
    return data

# parse category definition rules from user input
def parse_category_rules(rules):
    #TODO: check user input, sanitize, prepared statements?
    rules_array = [rule.strip() for rule in rules.strip().split(",")]
    parsed_rules = []
    for rule in rules_array:
        split_rule = rule.split(" ")
        split_rule = [token for token in split_rule if token != ""]
        label = split_rule[0][1:]
        split_rule = split_rule[1:]
        for num_token, token in enumerate(split_rule):
            if token.startswith("$"):
                split_rule[num_token] = 'row["' + token[1:] + '"]'
        statement = " ".join(split_rule)
        parsed_rules.append((label, statement))
    return parsed_rules

# add labels to data
def define_categories(data, default_label, rules):
    #TODO: variable 'row' is hardcoded, fix
    parsed_rules = parse_category_rules(rules)
    default_label = default_label.strip().replace(" ", "_")
    for dataset, _ in data:
            for experiment, _ in dataset:
                for num_link, (link, link_name) in enumerate(experiment):
                    defined_labels = []
                    for num_row, row in enumerate(link):
                        current_label = None
                        for label, statement in parsed_rules:
                            command = 'if ' + statement + ':\n    current_label = "' + label + '"'
                            exec(command)
                        if not current_label:
                            current_label = default_label
                        defined_labels.append(current_label)
                    experiment[num_link] = (append_fields(link, "class", defined_labels), link_name)
    print("Categories defined.")
    return data

def tokenize_for_export(data, out_format):
    tokens = []
    composition = {}
    out_names = []
    number_records = 0
    number_attributes = ["dataset_num", "experiment_num", "link_num"]
    attr_numbers = {}
    for key in number_attributes:
        attr_numbers[key] = 0

    for dataset, dataset_name in data:
        for experiment, experiment_name in dataset:
            for num_link, (link, link_name) in enumerate(experiment):
                number_rows = len(link)
                for link_column_name, link_column_type in link.dtype.descr:
                    link_column_values = link[link_column_name]
                    if link_column_name not in composition.keys(): 
                        composition[link_column_name] = {}
                        composition[link_column_name]["values"] = []
                        if link_column_name == "class":
                            data_type = "class"
                        else:
                            data_type = "numeric"
                        composition[link_column_name]["type"] = data_type
                        # TODO: support strings also
                        for _ in range(number_records):
                            composition[link_column_name]["values"].append("?")
                    
                    link_column_values = [str(value) for value in link_column_values]
                    composition[link_column_name]["values"].extend(link_column_values)

                new_number_records = number_records + number_rows
                if not all(key in composition.keys() for key in number_attributes):
                    for key in number_attributes:
                        composition[key] = {}
                        composition[key]["type"] = "class"
                        composition[key]["values"] = []
                for key in number_attributes:
                    for _ in range(number_records, new_number_records):
                        composition[key]["values"].append(str(attr_numbers[key]))

                if new_number_records > number_records:
                    for column_name, column_data in composition.items():
                        if len(column_data["values"]) < new_number_records:
                            for _ in range(number_records, new_number_records):
                                composition[column_name]["values"].append("?")

                number_records = new_number_records
                    
                attr_numbers["link_num"] += 1
                if out_format.upper() == "LINK":
                    for key in number_attributes:
                        del(composition[key])
                    tokens.append(composition)
                    out_names.append(dataset_name + "-" + experiment_name + "-" + link_name)
                    composition = {}
                    number_records = 0
            attr_numbers["experiment_num"] += 1
            if out_format.upper() == "EXPERIMENT":
                del(composition["dataset_num"], composition["experiment_num"])
                tokens.append(composition)
                out_names.append(dataset_name + "-" + experiment_name)
                composition = {}
                number_records = 0
        attr_numbers["dataset_num"] += 1
        if out_format.upper() == "DATASET":
            del(composition["dataset_num"])
            tokens.append(composition)
            out_names.append(dataset_name)
            composition = {}
            number_records = 0
    if out_format.upper() == "ALL":
        tokens.append(composition)
        out_names.append("output")

    return tokens, out_names

# writes the data to arff files
def export_to_file(data, out_format, out_path=OUT_PATH):
    # prepare data for output
    tokens, out_names = tokenize_for_export(data, out_format)
    if not tokens:
        print("Wrong output format specified.")
        print("Nothing outputted.")
        return

    # empty the output directory
    for file in os.listdir(out_path):
        file_path = os.path.join(out_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
    
    # output to files
    for token, name in zip(tokens, out_names):
        f_out = open(os.path.join(out_path, name + ".arff"), "w")
        f_out.write("@RELATION " + name + "\n\n")
        
        feature_values_all = []
        for feature in sorted(token.keys(), reverse=True):
            feature_values_all.append(token[feature]["values"])
            f_out.write("@ATTRIBUTE " + feature + " ")
            if token[feature]["type"] == "class":
                nominal_values = set(token[feature]["values"])
                feature_type = "{" + ",".join(nominal_values) + "}"
            else:
                feature_type = "numeric"
            f_out.write(feature_type + "\n")
        
        f_out.write("\n@DATA\n")

        for feature_values in zip(*feature_values_all):
            f_out.write(",".join(feature_values) + "\n")

        f_out.close()
    print("Files are successfully generated!")

    


if __name__ == "__main__":
    # select the input data, i.e. the datasets and experiments, and import it
    datasets, experiments = select_datasets_experiments()
    data = import_datasets_experiments(datasets, experiments)

    # TODO: filter by links/experiments
    pass
    
    # calculate other features (calculate new attributes, instant RSSI, avg RSSI, std, PRR, ch. memory, ...)
    print("Calculate other features? (y/n)")
    if raw_input().upper() == "Y":
        print("Input the PRR window. Leave blank to ommit.")
        prr_window = raw_input()
        prr_window = prr_window if prr_window != "" else None
        
        print("Input for which attributes you would like to calculate average/standard deviation feature in the following format: attr:avg/std:window.")
        print("To calculate more features, separate the inputs by a comma. Transformations will be applied in sequential order. New features are named in the following manner: attr_mode. Leave blank to ommit.")
        # TODO: dynamic possible attributes output
        #print("Available attributes: rssi, snr, prr, ...")
        avg_std = raw_input()
        avg_std = avg_std if avg_std != "" else None

        print("Enter the number of leading samples to truncate. Leave blank to ommit.")
        skip_leading = raw_input()
        skip_leading = skip_leading if skip_leading != "" else None

        '''
        ignore_last_window = False
        print("Input a window for aggregation/subsampling. Leave blank to ommit.")
        aggr_window = raw_input()
        if aggr_window == "":
            aggr_window = None
        else:
            print("Ignore the last window (underflow)? (y/n)")
            if raw_input().upper() == "Y":
                ignore_last_window = True
        '''
        # normalize 
        pass

        data = feature_enrichment(data, prr_window, avg_std, skip_leading)
    
    # define categories
    print("Define categories? (y/n)")
    if raw_input().upper() == "Y":
        print("Input the default label.")
        default_label = raw_input()
        if default_label != "":
            print("Input rules for labeling the samples. Rules will be applied in sequential order. Separate the rules with a comma.")
            print('Rules must be in the following format: #label1 $rssi < -50 [and $rssi > 90[,#label2 $attr3 == 10]]')
            print("All tokens must be separated with a space. Attribute names must begin with a $ (dollar) sign.")
            rules = raw_input()
            if rules != "":
                data = define_categories(data, default_label, rules)
            else:
                print("Categories not defined. No rule specified.")
        else:
            print("Categories not defined. No default label.")
    
    # TODO: perhaps do more filtering?
    pass

    # select the output format (LINK, EXPERIMENT, DATASET, ALL)
    # output to arff files
    print("Input the format of the output files (possible options: [link|experiment|dataset|all].")
    print("WARNING: THIS WILL DELETE ALL CONTENTS OF OUTPUT DIRECTORY!")
    out_format = raw_input()
    out_format = out_format if out_format != "" else None
    if out_format:
        export_to_file(data, out_format)
    else:
        print("Nothing outputted.")
