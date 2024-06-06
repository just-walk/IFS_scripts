#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Assembles flux spectra from QL GENE runs

"""

import argparse
import genelib as gl
import ql_tools as ql

parser = argparse.ArgumentParser()
parser.add_argument("ql_params", type=str, nargs="+", help="quasilinear run list")
parser.add_argument(
    "--stime", "-s", action="store", type=float, default=0, help="start time window"
)
parser.add_argument(
    "--etime", "-e", action="store", type=float, default=999999, help="end time window"
)
parser.add_argument(
    "--nrg_cols", "-C", type=tuple, default=(4, 6, 5, 7), help="nrg columns to include"
)
parser.add_argument(
    "--output",
    "-o",
    type=str,
    default="spectra_ql",
    help="output spectra file QL run",
)

# Parse arguments
args = parser.parse_args()
ql_params = args.ql_params
stime = args.stime
etime = args.etime
time_range = (stime, etime)
ql_runs = [gl.GENERun(par) for par in ql_params]

for run in ql_runs:
    run.read_parameters()
nrg_avg_t, _, oor_list = ql.nrg_time_average(ql_runs, time_range)
flxs_avg_t = nrg_avg_t[:, :, args.nrg_cols] # [ky, spec, fluxes]

ql.output_fluxes(flxs_avg_t, ql_runs, args.output)
