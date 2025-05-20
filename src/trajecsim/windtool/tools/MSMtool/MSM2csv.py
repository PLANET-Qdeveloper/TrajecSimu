#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 29 22:42:24 2018

@author: shugo
"""

import urllib.request
import numpy as np
import subprocess
import argparse
import os

from . import convert

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

def MSM2csv(year, month, day, init_time, fore_time, output_dir, wgrib2_exec_path='wgrib2'):
    this_file_path = os.path.abspath(os.path.dirname(__file__))

    date_str = '{yyyy}{mm:02}{dd:02}'.format(yyyy=year, mm=month, dd=day)
    folder_name = 'bin/JST' + str(init_time) + '+' + str(fore_time) + 'h/'
    bin_name = date_str + '_init' + str(init_time) + '+' + str(fore_time) + '.bin'
    bin_path = os.path.join(this_file_path, folder_name, bin_name)

    # convert bin to csv via wgrib2
    rawcsv_foldername = os.path.join(this_file_path, 'tmp/')
    rawcsv_filename = 'MSM_' + date_str + '_init' + str(init_time) + '+' + str(fore_time) + '_raw.csv'
    rawcsv_path = os.path.join(rawcsv_foldername, rawcsv_filename)

    if not os.path.exists(rawcsv_foldername):
        os.makedirs(rawcsv_foldername)

    if fore_time == 0:
        # ':anl:' indicates fore_time = 0
        flag_fore = ':anl:'
    else:
        flag_fore = ':' + str(fore_time) + ' hour fcst:'
    # END IF

    #wgrib2_abspath = os.path.abspath(wgrib2_exec_path)
    cmd = [wgrib2_exec_path, '-match', flag_fore, bin_path, '-csv', rawcsv_path]
    print('wgrib2 cmd echo:', ' '.join(cmd) )
    subprocess.run(cmd)

    if not os.path.exists(rawcsv_path):
        raise EnvironmentError('Failed to complete to execute wgrib2.')

    print('converting more coherent csv format')
    csv_output_foldername = output_dir
    csv_output_filename = 'MSM_' + date_str + '_init' + str(init_time) + '+' + str(fore_time) + '.csv'
    csv_output_path = os.path.join(csv_output_foldername, csv_output_filename)
    if not os.path.exists(csv_output_path):
        if not os.path.exists(csv_output_foldername):
            os.makedirs(csv_output_foldername)
        convert.convert_csv(rawcsv_path, csv_output_path)
        print('done converting')
        print('-----------------------')
    else:
        print('converted csv already exist.')
        print('-----------------------')
    os.remove(rawcsv_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ダウンロードしたMSMバイナリをcsvに変換')
    parser.add_argument('year_range')
    parser.add_argument('month_range')
    parser.add_argument('day_range')
    parser.add_argument('init_time')
    parser.add_argument('forecast_time')
    parser.add_argument('--wgrib2_exec_path', default="wgrib2", help='Exec path of wgrib2. default:"wgrib2"')

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
                date_str = '{yyyy}{mm:02}{dd:02}'.format(yyyy=y, mm=m, dd=d)
                for h in init_times:
                    for f in fore_times:
                        csv_output_foldername = 'csv/JST' + str(h) + '+' + str(f) + 'h/'
                        MSM2csv(y, m, d, h, f, output_dir=csv_output_foldername, wgrib2_exec_path=args.wgrib2_exec_path)
                        