#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for reading a list of input files (.dat or ####) and 
computing the average of the fluxes over a given time window
"""

import argparse
import numpy as np
from get_nrg import get_nrg0
from balloon_lib import check_suffix
from nrg_tools import nrg_averager

parser = argparse.ArgumentParser()
parser.add_argument("runlist", type=str, nargs="+", help="list of run numbers to read")
parser.add_argument(
    "--stime", "-s", action="store", type=float, default=0, help="start time window"
)
parser.add_argument(
    "--etime", "-e", action="store", type=float, default=999999, help="end time window"
)
parser.add_argument(
    "--nspec", "-n", action="store", type=int, default=2, help="number of species"
)
parser.add_argument(
    "--avg", "-a", action="store_true", default=False, help="average over runs"
)

args = parser.parse_args()

runlist = args.runlist
stime = args.stime
etime = args.etime
nspec = args.nspec
time_range = (stime, etime)

avg_nrg, _, oor_list = nrg_averager(runlist, time_range, nspec)
avg_flxs = avg_nrg[:, 4:8]

if len(runlist) > 1:
    flxs = np.delete(avg_flxs, oor_list, axis=0)
    if args.avg:
        mean_flxs = np.mean(flxs, axis=0)
        print(np.squeeze(mean_flxs))
    else:
        print(np.squeeze(flxs))
else:
    print(np.squeeze(avg_flxs))
