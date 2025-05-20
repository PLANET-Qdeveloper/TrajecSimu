#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 11 2019

@author: yamamotsu
"""

import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import os
import traceback
import argparse
import sonde_sites


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


def getSondeRequestUrl(station_name, year, month, day, hour):
    # default URL
    region_id = sonde_sites.getRegionID(station_name)
    url1 = "http://www.data.jma.go.jp/obd/stats/etrn/upper/view/daily_uwd.php?"
    url2 = "year="+str(year)+"&month="+str(month)+"&day="+str(day)+"&hour="+str(hour)
    url3 = "&atm=&point="+str(region_id)+"&view="
    return url1+url2+url3


def getSondeDataAsDataFrame(station_name, year, month, day, hour):
    request_url = getSondeRequestUrl(station_name, year, month, day, hour)

    df = pd.io.html.read_html(request_url, header=0)
    df = df[0]
    df = df.rename(columns = {
        '気圧(hPa)':'hPa',
        'ジオポテンシャル高度(m)':'GEO_HGT',
        '風速(m/s)':'SPEED',
        '風向(°)':'DIRECTION_DEGREE',
        '識別符':'IDENTIFICATION'
    })
    
    df = df.replace('特異点', 'singular point')
    df = df.replace('-', 0)
    df = df.replace('///', 0)

    df = df.astype({
        'SPEED': 'float32',
        'DIRECTION_DEGREE':'float32',
        'GEO_HGT': 'float32'
        }
        )
    return df


def convertSondeDataFormat(sonde_df):
    theta = sonde_df['DIRECTION_DEGREE'] * np.pi/180.0
    speed = sonde_df['SPEED']
    wind_u = np.array(-speed*np.sin(theta))
    wind_v = np.array(-speed*np.cos(theta))

    new_df = pd.DataFrame({
        'altitude': sonde_df['GEO_HGT'],
        'wind_u': wind_u,
        'wind_v': wind_v,
        'wind_speed': speed,
        'wind_direction_degree': sonde_df['DIRECTION_DEGREE']
    })
    return new_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ラジオゾンデ観測データをダウンロードするスクリプト')

    parser.add_argument('station_name')
    parser.add_argument('year_range')
    parser.add_argument('month_range')
    parser.add_argument('day_range')
    parser.add_argument('hour')

    parser.add_argument('--output_dir', default='wind_Rawin')

    args = parser.parse_args()

    station_name = args.station_name
    year_range = [int(y) for y in args.year_range.split(':')]
    month_range = [int(m) for m in args.month_range.split(':')]
    day_range = [int(d) for d in args.day_range.split(':')]
    hour = int(args.hour)

    years = getRange(year_range)
    months = getRange(month_range)
    days = getRange(day_range)

    savedir = os.path.join(this_file_path, '../', args.output_dir, station_name)
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    for y in years:
        for m in months:
            for d in days:
                date_str = '{:0>4}{:0>2}{:0>2}{:0>2}'.format(y, m, d, hour)
                csv_filename = os.path.join(savedir, 'Rawin_'+date_str+'.csv')
                df = getSondeDataAsDataFrame(station_name, y, m, d, hour)
                df_converted = convertSondeDataFormat(df)
                df_converted.to_csv(csv_filename, encoding='utf-8')
    
    print('OK')