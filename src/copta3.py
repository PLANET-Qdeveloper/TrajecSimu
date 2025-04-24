#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022/05/31

@author: hojo
"""

# sample driver script for trajectory simulation

import numpy as np
from Scripts.interface import TrajecSimu_UI

# define path and filename of raa csv file
config_filename = 'Parameters_csv/copta3.csv'

# create an instance
mysim = TrajecSimu_UI(config_filename, 'izu')

# ------------------------------------
# run a single trajectory computation
# ------------------------------------
mysim.run_single()

# ------------------------------------
# run a loop for landing point distribution
# ------------------------------------
# format: run_loop(n_winddirec, max_windspeed, windspeed_step)
#         n_winddirec: number of wind directions
#         max_windspeed: max. wind speed [m/s]
#         windspeed_step: wind speed step [m/s]
#mysim.run_loop(4, 4, 1)

# ------------------------------------
# run an inverse design problem
# ------------------------------------
#estimate engine property required max Mach=1.0 with m_dry = 20.
#mysim.run_rapid_design(m_dry=20., obj_type='Mach', obj_value=1.1)
