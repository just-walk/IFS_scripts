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

VARNAMES = (
    r"$|n|^2$",
    r"$|u_\parallel|^2$",
    r"$T_\parallel$",
    r"$T_\perp$",
    r"$\Gamma_\text{es}^x$",
    r"$\Gamma_\text{em}^x$",
    r"$Q_\text{es}^x$",
    r"$Q_\text{em}^x$",
    r"$\Pi_\text{es}^x$",
    r"$\Pi_\text{em}^x$",
)


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


def output_fluxes(nrg_data, pars, nrg_cols):
    """Output flux data for multiple ky in separate files for each species"""
    ky_list = np.zeros((nrg_data.shape[0], 1))
    for j, par in enumerate(pars):
        ky_list[j] = par["kymin"]
    for i in range(nrg_data.shape[1]):
        spec = par["name" + str(i + 1)]
        filename = "avg_nrg_" + spec
        head = "$k_y$ "
        for col in nrg_cols:
            head += VARNAMES[col] + " "
        header = head[:-1]  # remove trailing space
        data = np.concatenate((ky_list, np.squeeze(nrg_data[:, i, :])), axis=1)
        np.savetxt(
            filename,
            data,
            fmt="%E",
            header=header,
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
