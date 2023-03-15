#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module with some tools for reading and manipulating data from nrg files
"""

import numpy as np
from get_nrg import get_nrg0
from balloon_lib import check_suffix


def nrg_averager(runlist, time_range, nspec):
    """
    Function for reading a list of input files (.dat or ####) and
    computing the average of the nrg variables over a given time window
    """

    stime = time_range[0]
    etime = time_range[1]

    avg_nrg = np.zeros([len(runlist), nspec, 10])
    oor_list = []

    for irun, run in enumerate(runlist):
        suffix = check_suffix(run)
        out_list = list(get_nrg0(suffix, nspec))
        times = np.array(out_list[0])
        nrg_arr = np.array(out_list[1:])
        time_rng = np.nonzero((stime < times) & (times < etime))[0]
        if time_rng.size == 0:
            print("Run " + suffix + " has no times within range. Skipping...")
            oor_list.append(irun)
            continue
        nrg_time = nrg_arr[:, time_rng, :]
        avg_nrg[irun] = np.mean(nrg_time, axis=1)

    return np.squeeze(avg_nrg), nrg_time, oor_list
