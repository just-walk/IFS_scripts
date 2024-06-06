#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module with some tools for reading and manipulating data from nrg files
"""

from itertools import groupby
import numpy as np
from get_nrg import get_nrg0
import matplotlib.pyplot as plt
import genelib as gl

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

VARNAME_MAP = (0, 4, 6, 5, 7)  # map fluxspectra column indices to VARNAMES


def nrg_time_average(runlist, time_range):
    """
    Function for reading a list of input files (.dat or ####) and
    computing the average of the nrg variables over a given time window
    """

    stime = time_range[0]
    etime = time_range[1]

    nspec = runlist[0].pars["box"]["n_spec"]
    avg_nrg = np.zeros([len(runlist), nspec, 10])
    oor_list = []

    for irun, run in enumerate(runlist):
        suffix = gl.check_suffix(run.runnumber)
        out_list = list(get_nrg0(suffix, nspec, path=run.dir_path))
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


def read_fluxes(filename):
    """Open avg_nrg file (from ql_tools.py) and return as array"""
    return np.loadtxt(filename)


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


def create_spec_coefs(nl_fluxes, flxs_avg, ql_runs):
    ky_list = np.zeros((flxs_avg.shape[0], 1))
    for j, run in enumerate(ql_runs):
        ky_list[j] = run.pars["box"]["kymin"]
    spec_coef_dict = {}
    for i in range(ql_runs[0].pars["box"]["n_spec"]):  # take n_spec from first par dict
        spec = ql_runs[0].pars["species"][i]["name"]
        ql_flux = np.concatenate((ky_list, np.squeeze(flxs_avg[:, i, :])), axis=1)
        spec_coef_dict[spec] = create_spec_coef(nl_fluxes[spec][1], ql_flux)
    return spec_coef_dict


def create_spec_coef(nl_flux, ql_flux, ifplot=False):
    """Interpolates NL flux data to QL k values, calculates scaling for each"""
    k_nl = nl_flux[1:, 0]
    k_ql = ql_flux[:, 0]

    spec_coef = np.zeros((k_ql.size, 5))
    spec_coef[:, 0] = k_ql

    for col in range(1, spec_coef.shape[1]):
        f = np.interp(k_ql, k_nl, nl_flux[1:, col])
        spec_coef[:, col] = f / ql_flux[:, col]

    if ifplot:
        plt.title(r"Spec_Coef function")
        plt.xlabel("ik")
        plt.ylabel(r"$S(ik)$")
        for col in range(1, spec_coef.shape[1]):
            plt.plot(k_nl, nl_flux[1:, col], label="NL, " + VARNAMES[VARNAME_MAP[col]])
        for col in range(1, spec_coef.shape[1]):
            plt.plot(k_ql, ql_flux[:, col], label="QL, " + VARNAMES[VARNAME_MAP[col]])
        for col in range(1, spec_coef.shape[1]):
            plt.plot(k_ql, spec_coef[:, col], label="S, " + VARNAMES[VARNAME_MAP[col]])
        plt.legend()
        plt.show()

    return spec_coef


def plot_spec_coef(spec_coef):
    plt.title(r"Spec_Coef function")
    plt.xlabel("ik")
    plt.ylabel(r"$S(ik)$")
    plt.plot(spec_coef)
    plt.show()


def output_spec(spec, varname):
    """Output spectrum for multiple ky"""
    header = "\tky\t" + varname
    filename = "./" + varname + ".dat"
    np.savetxt(
        filename,
        spec,
        fmt="% E",
        header=header,
        encoding="UTF-8",
    )


def read_spec(filename):
    """Read spectrum for multiple ky"""
    spec = np.loadtxt(filename)
    return spec


def output_spec_coef(spec, varname):
    """Output spec_coef function for multiple ky"""
    head = "$k_y$ "
    for col in range(1, spec.shape[1]):
        head += VARNAMES[VARNAME_MAP[col]] + " "
    header = head[:-1]  # remove trailing space
    filename = "./" + varname + ".dat"
    np.savetxt(
        filename,
        spec,
        fmt="% E",
        header=header,
        encoding="UTF-8",
    )


# def parse_runnumber(filepath):
#     return re.search(r"([0-9]{1,4})$", filepath).group(0)


def read_genediag_fluxes(generun: gl.GENERun):
    flux_dict = {}
    for i in range(generun.pars["box"]["n_spec"]):
        specname = generun.pars["species"][i]["name"]
        if generun.suffix == ".dat":
            filename = generun.dir_path + "fluxspectra" + specname + "_act.dat"
        else:
            filename = (
                generun.dir_path + "fluxspectra" + specname + "_" + generun.suffix
            )
        # flux_list.append(read_fluxspectra(filename))
        flux_dict[specname] = read_fluxspectra(filename)
    return flux_dict


# class NLRun(gl.GENERun):
#     """Extension of GENERun object to include additional data structures"""

#     def __init__(self, parameters_filepath: str):
#         super().__init_(parameters_filepath)

#     def init_fluxarrays(self):
#         self.flux.


def create_new_pars_dict(generun, spec_coefs, avg=True):
    s = ""
    for i in range(generun.par["box"]["n_spec"]):
        specname = pars["species"][i]["name"]


def update_ql_coefs(run: gl.GENERun, coefs, index):
    # patch_nml = {"general": {"ql_D": coefs}}
    # f90nml.patch(self.par_path, patch_nml, self.par_path + "_new")
    # for i in range(self.pars["box"]["n_spec"]):
    for i, spec in enumerate(coefs):
        try:
            spec == run.pars["species"][i]["name"]
        except ValueError:
            print("species namelists are incorrectly ordered")
        run.pars["species"][i]["qlG"] = coefs[spec][index][1]
        run.pars["species"][i]["qlQ"] = coefs[spec][index][2]
