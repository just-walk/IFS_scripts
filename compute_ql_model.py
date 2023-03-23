#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for computing the predicted QL heat flux from a pre-computed shape
function file and corresponding fluxspectra files from GENE IDL diagnostic
"""

import argparse
import nrg_tools as nrg
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("shape_file", type=str, help="flux spectrum shape function")
parser.add_argument(
    "flux_files", nargs="+", type=str, help="quasilinear flux spectra (from IDL diag)"
)

args = parser.parse_args()

shape_func = nrg.read_spec(args.shape_file)

fluxes = []
total_fluxes =[]
for flux_file in args.flux_files:
    flux = nrg.read_fluxspectra(flux_file)[1]
    fluxes.append(flux)
    total_flux = np.sum(shape_func[:,1]*flux[1:,2])/74.75*51.8
    total_fluxes.append(total_flux)

print(total_fluxes)
