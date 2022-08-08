#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import genelib as glib
import ParIO as pario
import fieldlib
import momlib
import matplotlib.pyplot as plt
import balloon_lib as bl
import read_write_geometry as rwg
import finite_differences as fd

parser = argparse.ArgumentParser()
parser.add_argument("suffix", help="run number or .dat suffix of output data")
parser.add_argument("geom", help="geometry file")
parser.add_argument(
    "--global", "-g", action="store_true", help="global geometry (default local)"
)

args = parser.parse_args()

suffix = bl.check_suffix(args.suffix)

par = pario.Parameters()
par.Read_Pars("parameters" + suffix)
pars = par.pardict

parameters, geometry = rwg.read_geometry_global(args.geom)

field = fieldlib.fieldfile("field" + suffix, pars)

stime = 0
etime = 1e5
ftimes = bl.get_times(field, stime, etime)

times = ftimes[-1]  # final time only

# print("Analyzing for times: ", times)

field = fieldlib.fieldfile("field" + suffix, pars)

phi = np.squeeze(field.phi())

lx = pars["lx"]
ky = pars["kymin"]

nx = field.nx
nz = field.nz

xgrid = np.linspace(0, lx, nx)


def calc_kx(field, xgrid):
    dfielddx = fd.fd_d1_o4(field, xgrid)
    kx = dfielddx
    return kx


def calc_kx2(field, xgrid):
    d2fielddx2 = fd.fd_d2_o4(field, xgrid)
    kx2 = d2fielddx2
    return kx2


def calc_kperp(field, xgrid, ky, nz, geometry):
    gxx = geometry["gxx"]
    gxy = geometry["gxy"]
    gyy = geometry["gyy"]
    jac = geometry["jacobian"]

    kx = calc_kx(field, xgrid)
    kx2 = calc_kx2(field, xgrid)

    # kperp2 = gxx * np.abs(kx) ** 2 + 2 * gxy * np.abs(kx) * ky + gyy * ky**2
    # kperp2_avg = np.sum((jac * kperp2).flatten()) / np.sum(jac.flatten())
    # print("kperp2_avg = ", kperp2_avg)

    kperp2 = gxx * np.abs(kx2) + 2 * gxy * kx * ky + gyy * ky**2
    kperp2_avg = np.sum((jac * kperp2).flatten()) / np.sum(jac.flatten())
    # print("kperp2_avg = ", np.abs(kperp2_avg))

    # print("|kx|, ky = ", np.abs(kx), ky)
    return kperp2_avg


kperp2 = calc_kperp(phi, xgrid, ky, nz, geometry)
print(abs(kperp2))
