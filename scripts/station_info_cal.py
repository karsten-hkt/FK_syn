# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2025/4/11 14:50
@Author : karsten
@File : station_info_cal.py
@Software: PyCharm
============================
"""
from obspy.geodetics.base import gps2dist_azimuth, kilometer2degrees
import math
import obspy

real_sac_locate = '../input/real_obs_sac'

st = obspy.read(real_sac_locate+'/*XZ.*Z.*SAC')
for tr in st:
	st_stla = tr.stats.sac.stla
	st_stlo = tr.stats.sac.stlo
	point_eq_evla = tr.stats.sac.evla # lat
	point_eq_evlo = tr.stats.sac.evlo  # lon
	print(point_eq_evla,point_eq_evlo)
	dist, azim, back_azim = gps2dist_azimuth(point_eq_evla, point_eq_evlo, st_stla,
	                                                     st_stlo)
	print(f"{tr.stats.network}.{tr.stats.station} {round(dist/1000, 2)} {round(azim, 2)}")