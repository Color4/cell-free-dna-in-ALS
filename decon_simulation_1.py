# 29 aug 17
# simple script to produce simulated observed and reference data
# for given mixtures of origin tissue
# author <christa.caggiano@ucsf.edu>

import numpy as np
import argparse
import random


def choose_random_cases(case):

    """
    pseudo-randomly decide if a case should be selected
    :param case: number of cases (individual or cpgs)
    :return: a dict that contains a bool (0 or 1) indicating whether or not case is selected
    """

    case_dict = dict.fromkeys(range(cpg))  # generate dict where the keys are the cpgs of interest

    for case in case_dict:  # for each cpg pick a 0 or 1 and assign it as the value
        case_dict[case] = random.randint(0, 1)
    return case_dict


def create_array(case_dict, mean, sd, max, size, distribution_type, scaling, column_stack):
    """
    creates an array where if a particular case is selected, values are generated around a given distribution
    otherwise values are generated so that they are similar, with a small degree of noise
    :param case_dict: either cpg or individual dictionaries that indicate which cases should be selected
    :param mean:
    :param sd:
    :param max:
    :param size: number of values to be generated
    :param distribution_type:
    :param column_stack: bool value indicating how to appropriately arrange the data
    :return: an array containing values (methylation or cell type proportions) that have a particular distribution
    """
    array_list = [[] for i in range(size)]

    for case in range(len(case_dict)):
        if case_dict[case] == 1:
            array_list[case] = distribution_type(mean, sd, size)*scaling
        else:
            static_value = max / 100 * random.randint(10, 99)
            array_list[case] = [static_value + random.choice(np.arange(-(static_value/10), static_value/10, scaling/10)) for i in range(size)]
    if column_stack:
        return np.column_stack(array_list)
    else:
        return np.vstack(array_list)

if __name__ == "__main__":

    # accepts user input
    # all choices must be greater than 1
    # default is 5 individuals, 3 tissues, and 3 CpGs
    parser = argparse.ArgumentParser()
    parser.add_argument("--individuals", help="number of individuals", type=int, choices=range(2,100), default=5)
    parser.add_argument("--tissues", help="number of tissues", type=int, choices=range(2,100), default=3)
    parser.add_argument("--cpgs", help="number of CpG sites", type=int, choices=range(2,100), default=3)

    args = parser.parse_args()

    individual = args.individuals
    cpg = args.cpgs
    tissue = args.tissues

    # hardcoded mean and sd from methylation data set mentioned in refactor paper
    # TODO change this to something better
    mean = 7000
    maximum = 60000
    sd = 435

    cpg_dict = choose_random_cases(cpg)  # select random cpgs to be differentially methylated
    individual_dict = choose_random_cases(individual)  # select individuals to have non-normal levels of cfDNA

    # creates a reference array where methylation values are normally distributed if they are differentially methylated
    # and base these methylation values around the descriptive statistics of the aforementioned data set
    ref_array = create_array(cpg_dict, mean, sd, maximum, tissue, np.random.normal, 1, True)

    # create an array of cell proportions for each individual where proportions have a lognormal(skewed) distribution
    # indicating a non-normal (perhaps disease) state
    cell_proportion_array = create_array(individual_dict, 2, 0.2, 1, cpg, np.random.lognormal, 0.1, False)
    print(ref_array)
    print(cell_proportion_array)