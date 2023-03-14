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

args = parser.parse_args()

runlist = args.runlist
stime = args.stime
etime = args.etime
nspec = args.nspec

nrun = len(runlist)

avg_flxs = np.zeros([nrun, nspec, 4])
oor_list = []

for irun, run in enumerate(runlist):
    suffix = check_suffix(run)
    out_list = list(get_nrg0(suffix, nspec))
    times = np.array(out_list[0])
    nrg_arr = np.array(out_list[1:])
    flxs_arr = nrg_arr[:, :, 4:8]
    time_rng = np.nonzero((stime < times) & (times < etime))[0]
    if time_rng.size == 0:
        print("Run " + suffix + " has no times within range. Skipping...")
        oor_list.append(irun)
        continue
    flxs_time = flxs_arr[:, time_rng, :]
    avg_flxs[irun] = np.mean(flxs_time, axis=1)

if nrun > 1:
    mean_flxs = np.mean(np.delete(avg_flxs, oor_list, axis=0), axis=0)
    print(np.squeeze(mean_flxs))
else:
    print(np.squeeze(avg_flxs))
