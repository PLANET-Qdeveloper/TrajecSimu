#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 22:42:24 2018

@author: shugo
"""

import urllib.request
import numpy as np
import datetime
import argparse
import os

def getRange(range_array):
    if len(range_array) == 3:
        array = np.arange(range_array[0], range_array[1]+1, range_array[2])
    elif len(range_array) == 2:
        array = np.arange(range_array[0], range_array[1]+1)
    elif len(range_array) == 1:
        array= np.array([range_array[0]])
    else:
        array = np.array([])
    return array

def downloadMSM(year, month, day, init_time, fore_time, output_dir):
    JST = datetime.timedelta(hours=+9)
    time_JST = datetime.datetime(year, month, day, init_time)
    time_UTC = time_JST - JST
    fore_time_delta = datetime.timedelta(hours=int(fore_time))
    print('initial time:')
    print('  in UTC: ', time_UTC)
    print('  in JST: ', time_JST)
    print('forecast time after initial time:')
    print('  in JST: ', time_JST + fore_time_delta)

    # --------------------
    # download MSM forecast file
    # --------------------
    # bin filename to download
    #time_str = '{yyyy}{mm:02}{dd:02}{hh:02}0000'.format(yyyy=y, mm=m, dd=d, hh=init_time)
    time_str = time_UTC.strftime('%Y%m%d%H')
    if fore_time <= 15:
        FH_str = '00-15'
    elif fore_time <= 33:
        FH_str = '18-33'
    else:
        FH_str = '36-39'

    bin_name = 'Z__C_RJTD_' + time_str + '0000_MSM_GPV_Rjp_L-pall_FH' + FH_str + '_grib2.bin'

    print('Downloading bin filename: ', bin_name)
    print('-----------------------')

    # url to access
    home_url = 'http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/original/'
    date_url = time_UTC.strftime('%Y/%m/%d/')
    url = home_url + date_url + bin_name

    #bin_output_foldername = 'bin/JST' + str(time_JST.hour) + '+' + str(f) + 'h/' 
    bin_output_foldername = output_dir
    bin_output_name = time_JST.strftime('%Y%m%d_init%H+{}.bin'.format(fore_time))
    output_path = os.path.join(bin_output_foldername, bin_output_name)
    if os.path.exists(output_path):
        print('the bin file is already exists.')
        return

    if not os.path.exists(bin_output_foldername):
        os.makedirs(bin_output_foldername)
    # download into cd
    urllib.request.urlretrieve(url,output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MSMデータをダウンロードするスクリプト')

    parser.add_argument('year_range')
    parser.add_argument('month_range')
    parser.add_argument('day_range')
    parser.add_argument('init_time')
    parser.add_argument('forecast_time')

    args = parser.parse_args()

    year_range = [int(y) for y in args.year_range.split(':')]
    month_range = [int(m) for m in args.month_range.split(':')]
    day_range = [int(d) for d in args.day_range.split(':')]
    init_time_range = [int(h) for h in args.init_time.split(':')]
    forecast_time_range = [int(f) for f in args.forecast_time.split(':')]
    print(year_range, month_range, day_range, init_time_range, forecast_time_range)

    years = getRange(year_range)
    months = getRange(month_range)
    days = getRange(day_range)
    init_times = getRange(init_time_range)
    fore_times = getRange(forecast_time_range)

    # loop over years
    for y in years:
        # loop over monthes
        for m in months:
            # loop over days
            for d in days:
                for h in init_times:
                    for f in fore_times:
                        output_dir = 'bin/JST' + str(h) + '+' + str(f) + 'h/' 
                        downloadMSM(y, m, d, h, f, output_dir=output_dir)
