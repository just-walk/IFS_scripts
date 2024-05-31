#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for reading a list of input files (.dat or ####) and 
computing the ql shape function (coefficients for each ky)
"""

import argparse
import ql_tools as ql

parser = argparse.ArgumentParser()
parser.add_argument("nl_flux", type=str, help="nonlinear flux spectrum (from IDL diag)")
parser.add_argument(
    "ql_flux", type=str, help="quasilinear flux spectrum (from avg_nrg_[species] file)"
)
parser.add_argument(
    "--plot", "-p", action="store_true", default=False, help="print to stdout"
)

args = parser.parse_args()

nl_file = args.nl_flux
ql_file = args.ql_flux

nl_fluxes = ql.read_fluxspectra(nl_file)
ql_fluxes = ql.read_fluxes(ql_file)

shape_func = ql.create_shape(nl_fluxes[1], ql_fluxes, ifplot=args.plot)
ql.output_shape(shape_func, "ql_shape")
