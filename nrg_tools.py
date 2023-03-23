#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module with some tools for reading and manipulating data from nrg files
"""

from itertools import groupby
import numpy as np
from get_nrg import get_nrg0
from balloon_lib import check_suffix
import matplotlib.pyplot as plt

# try:
#     from scipy.interpolate import interp1d as interp
# except ImportError:
#     from numpy import interp


def nrg_time_average(runlist, time_range, nspec):
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

    if len(runlist) > 1:
        nrg_out = np.squeeze(np.delete(avg_nrg, oor_list, axis=0))
    else:
        nrg_out = np.squeeze(avg_nrg)

    return nrg_out, nrg_time, oor_list


def nrg_run_average(nrg_arr):
    """
    Function for performing simple mean over the first dimension
    """
    if nrg_arr.ndim < 2:
        raise ValueError("ndim must be greater than 1")

    avg_nrg = np.squeeze(np.mean(nrg_arr, axis=0))
    return avg_nrg


def output_nrg(nrg_data, filename):
    """Output nrg_data for multiple ky"""
    # header = (
    #     varname
    #     + "\t"
    #     + "first row is "
    #     + yvar["name"]
    #     + " and first column is "
    #     + xvar["name"]
    # )
    # tmp = np.insert(xvar["vlist"], 0, yvar["vlist"].size)
    # nrows = tmp.size - 1
    # column = np.array(tmp)[np.newaxis, :].T
    # data = np.hstack((column, np.vstack((yvar["vlist"], spec[:nrows, :]))))
    # varname = "nrg_flxs"
    # filename = "./" + varname + "_.dat"
    np.savetxt(
        filename,
        nrg_data,
        fmt="% E",
        # header=header,
        encoding="UTF-8",
    )


def read_fluxspectra(filename):
    """Reads fluxspectra file, outputting kx, ky spectra as two arrays in a list"""
    array_list = []

    with open(filename) as f_data:
        for k, g in groupby(f_data, lambda x: x.startswith("#")):
            if not k:
                array_list.append(
                    np.array(
                        [[float(x) for x in d.split()] for d in g if len(d.strip())]
                    )
                )

    return array_list


def create_shape(nl_flux, ql_flux, ifplot=False):
    """Interpolates NL flux data to QL k values, calculates scaling for each"""
    k_nl = nl_flux[1:, 0]
    k_ql = ql_flux[1:, 0]
    Q_nl = nl_flux[1:, 2]
    Q_ql = ql_flux[1:, 2]

    f = np.interp(k_ql, k_nl, Q_nl)

    shape = np.array([k_ql, f / Q_ql])

    if ifplot:
        plt.title(r"Shape function")
        plt.xlabel("ik")
        plt.ylabel(r"$S(ik)$")
        plt.plot(k_nl, Q_nl)
        plt.plot(k_ql, Q_ql)
        plt.plot(k_ql, shape[:, 1])
        plt.show()

    return shape


def plot_shape(shape):
    plt.title(r"Shape function")
    plt.xlabel("ik")
    plt.ylabel(r"$S(ik)$")
    plt.plot(shape)
    plt.show()


def output_spec(spec, varname):
    """Output spectrum for multiple ky"""
    header = "\tky\t" + varname
    filename = "./" + varname + ".dat"
    np.savetxt(
        filename,
        spec.T,
        fmt="% E",
        header=header,
        encoding="UTF-8",
    )


def read_spec(filename):
    """Output spectrum for multiple ky"""
    spec = np.loadtxt(filename)
    return spec
