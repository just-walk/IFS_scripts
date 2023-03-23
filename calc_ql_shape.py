#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for reading a list of input files (.dat or ####) and 
computing the average of the fluxes over a given time window
"""

import argparse
import nrg_tools as nrg

parser = argparse.ArgumentParser()
parser.add_argument("nl_flux", type=str, help="nonlinear flux spectrum (from IDL diag)")
parser.add_argument(
    "ql_flux", type=str, help="quasilinear flux spectrum (from IDL diag)"
)

args = parser.parse_args()

nl_file = args.nl_flux
ql_file = args.ql_flux

nl_fluxes = nrg.read_fluxspectra(nl_file)
ql_fluxes = nrg.read_fluxspectra(ql_file)

shape_func = nrg.create_shape(nl_fluxes[1], ql_fluxes[1])
nrg.output_spec(shape_func, "ql_shape")
