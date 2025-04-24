
import urllib.request
import numpy as np
import subprocess
import argparse
import os
import sys

from . import convert

# 上位ディレクトリのモジュールをインポートするためにsys.pathに上位ディレクトリのパスを追加する
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sonde_sites import getSondeLocation

this_file_path = os.path.abspath(os.path.dirname(__file__))


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


def placeName2coord(place_name:str):
    if place_name == 'Izu-umi':
        point_coord = np.array([34.679730, 139.438373]) #izu-umi
    elif place_name == 'Noshiro-umi':
        point_coord = np.array([40.242865, 140.010450]) # noshiro-umi
    else:
        point_coord = getSondeLocation(place_name)
    return point_coord


def interpolateMSM(year, month, day, init_time, fore_time, place_name, output_dir):
    # -----------------
    # spacial interpolation at launch site
    # -----------------

    date_str = '{yyyy}{mm:02}{dd:02}'.format(yyyy=year, mm=month, dd=day)
    csv_foldername = 'csv/JST' + str(init_time) + '+' + str(fore_time) + 'h/'
    csv_filename = 'MSM_' + date_str + '_init' + str(init_time) + '+' + str(fore_time) + '.csv'
    csv_path = os.path.join(this_file_path, csv_foldername, csv_filename)

    place_coord = placeName2coord(place_name)

    print('-----------------------')
    print('spacial interp. at ', place_coord)
    print('                on ', date_str)

    interp_foldername = output_dir
    interp_filename = 'MSM_' + date_str + '{:0>2}'.format(init_time) + '+' + str(fore_time) + 'h.csv'
    interp_path = os.path.join(interp_foldername, interp_filename)
    if not os.path.exists(interp_foldername):
        os.makedirs(interp_foldername)
    
    # interpolate values at the site and write into csv.
    # the output file to be used in TrajecSimu code
    try:
        convert.interpolate_space(csv_path, interp_path, place_coord, plot_flag=True)
    except:
        print('ERROR. this file is ignored')
        return
    
    print('done interpolation')
    print('-----------------------')
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ダウンロード&csv変換したMSMファイルから指定した地点の風を抽出')

    parser.add_argument('year_range')
    parser.add_argument('month_range')
    parser.add_argument('day_range')
    parser.add_argument('init_time')
    parser.add_argument('forecast_time')

    parser.add_argument('place', help='風向風速を取りだす地点名。現在は"Izu-umi","Hachijo-jima","Noshiro-umi"から指定可能。')

    args = parser.parse_args()

    year_range = [int(y) for y in args.year_range.split(':')]
    month_range = [int(m) for m in args.month_range.split(':')]
    day_range = [int(d) for d in args.day_range.split(':')]
    init_time_range = [int(h) for h in args.init_time.split(':')]
    forecast_time_range = [int(f) for f in args.forecast_time.split(':')]
    interp_place = args.place

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
                        output_dir = 'interp_wind/' + interp_place + '/JST' + str(h) + '+' + str(f) + 'h/'
                        interpolateMSM(y, m, d, h, f, interp_place, output_dir)