#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import parIOWrapper as parw
import re


def check_suffix(run_number):
    if re.search("dat$", run_number):
        suffix = ".dat"
    elif re.search("[0-9]{1,4}$", run_number):
        match = re.search(r"([0-9]{1,4})$", run_number)
        suffix = "_" + match.group(0).zfill(4)
    else:
        ValueError("Please enter a valid run number, e.g. .dat or 0123")
    return suffix


class GENERun(object):
    """Documentation for GENERun object"""

    def __init__(self, parameters_filepath: str):
        self.init_paths(parameters_filepath)

    def init_paths(self, parameters_filepath):
        filepath = Path(parameters_filepath)
        self.dir_path = str(filepath.parent) + "/"
        self.par_path = str(filepath)
        self.suffix = check_suffix(parameters_filepath)
        self.runnumber = self.suffix.strip("_").strip(".")
        # print(self.runnumber)

    def read_parameters(self):
        self.pars = parw.create_parameters_dict(self.par_path)
