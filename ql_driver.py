#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for driving QL tools produce th coefficients for QL GENE

"""

import argparse
import genelib as gl
import ql_tools as ql

parser = argparse.ArgumentParser()
parser.add_argument("nl_param", type=str, help="nonlinear parameters file")
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
    default="parameters_new.dat",
    help="output parameters file for QL run",
)


# Parse arguments
args = parser.parse_args()
nl_param = args.nl_param
ql_params = args.ql_params
stime = args.stime
etime = args.etime
time_range = (stime, etime)

nl_run = gl.GENERun(nl_param)
nl_run.read_parameters()
print(nl_run.par_path)
ql_runs = [gl.GENERun(par) for par in ql_params]
runlist = []
for run in ql_runs:
    run.read_parameters()
    runlist.append(run.runnumber)
out_run = gl.GENERun(args.output)

# Read and time average fluxes from nrg files
nrg_avg_t, _, oor_list = ql.nrg_time_average(runlist, time_range, nl_run.pars["n_spec"])
flxs_avg_t = nrg_avg_t[:, :, args.nrg_cols]

# Read nonlinear fluxes
nl_fluxes = ql.read_genediag_fluxes(nl_run)

coefs = ql.create_spec_coefs(nl_fluxes, flxs_avg_t, ql_runs)

print(coefs["ions"])
print(coefs["electrons"])
