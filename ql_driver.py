#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for driving QL tools produce the coefficients for QL GENE

"""

import argparse
import genelib as gl
import ql_tools as ql
# import numpy as np

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
# print(nl_run.par_path)
ql_runs = [gl.GENERun(par) for par in ql_params]
runlist = []
kylist = []
for run in ql_runs:
    run.read_parameters()
    # print(run.pars)
    # print(run.par_path)
    runlist.append(run.runnumber)
    # kylist.append(run.pars["box"]["kymin"])
# out_run = gl.GENERun(args.output)
# out_run.pars = run.pars
# out_run.update_ky(kylist)
# print(out_run.pars)
# out_run.write_parameters()

# # print(out_run.pars)
# parout.Read_Pars(ql_params[0])
# # parout.pardict = out_run.pars
# # print(parout.pardict)
# parout.Write_Pars(out_run.par_path)

# Read and time average fluxes from nrg files
nrg_avg_t, _, oor_list = ql.nrg_time_average(
    runlist, time_range, nl_run.pars["box"]["n_spec"], run.dir_path
)
flxs_avg_t = nrg_avg_t[:, :, args.nrg_cols]

# Read nonlinear fluxes
nl_fluxes = ql.read_genediag_fluxes(nl_run)

coefs = ql.create_spec_coefs(nl_fluxes, flxs_avg_t, ql_runs)

for i, run in enumerate(ql_runs):
    ql.update_ql_coefs(run, coefs, i)
    run.write_parameters("parameters_" + run.runnumber + "_newql")
    # print(run.par_path)
    # print(run.dir_path)


print(coefs["ions"])
print(coefs["electrons"])

# print(np.mean(coefs["ions"], axis=0))
# print(np.mean(coefs["electrons"], axis=0))
