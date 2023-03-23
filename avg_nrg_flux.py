#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for reading a list of input files (.dat or ####) and 
computing the average of the fluxes over a given time window
"""

import argparse
import nrg_tools as nrg

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
parser.add_argument(
    "--print", "-p", action="store_true", default=False, help="print to stdout"
)
parser.add_argument(
    "--output", "-o", action="store_true", default=False, help="output to file"
)
parser.add_argument(
    "--nrg_cols", "-C", type=tuple, default=(4, 5, 6, 7), help="nrg columns to include"
)

args = parser.parse_args()

runlist = args.runlist
stime = args.stime
etime = args.etime
nspec = args.nspec
nrg_cols = args.nrg_cols
time_range = (stime, etime)

nrg_avg_t, _, oor_list = nrg.nrg_time_average(runlist, time_range, nspec)
flxs_avg_t = nrg_avg_t[:, nrg_cols]

if args.avg and len(runlist) > 1:
    flxs_avg_tr = nrg.nrg_run_average(flxs_avg_t)
else:
    flxs_avg_tr = flxs_avg_t

if args.print:
    print(flxs_avg_tr)

if args.output:
    nrg.output_nrg(flxs_avg_t)
