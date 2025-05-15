import os
import argparse
import datetime
import json
import numpy as np
from glob import glob
import pandas as pd
from tools.load_wind import loadWind

import matplotlib.pyplot as plt

this_file_path = os.path.abspath(os.path.dirname(__file__))


def getMSMWind(location, datetime, fore_time, interp_kind='linear'):
    dirname = 'wind_MSM/' + location + '/' + datetime.strftime('JST%H+') + str(fore_time) + 'h/'
    filename = datetime.strftime('MSM_%Y%m%d%H+') + str(fore_time) + 'h.csv'
    filepath = os.path.join(this_file_path, dirname, filename)
    return loadWind(filepath, interp_kind)


def getRawin(station_name, datetime, interp_kind='linear'):
    # ラジオゾンデcsvファイルから高度補完した風を生成
    dirname = 'wind_Rawin/' + station_name + '/'
    filename = datetime.strftime('Rawin_%Y%m%d%H.csv')
    filepath = os.path.join(this_file_path, dirname, filename)
    return loadWind(filepath, interp_kind)


def getStatParameters(wind):
    # input: wind[sample, elements]
    mean = wind.mean(axis=0)
    sigma = np.cov(wind.T)
    return mean, sigma


class TypeEncoder(json.JSONEncoder):
    # Numpyの型をそのままjsonにdumpすることができないので
    # それを対応させるクラス
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(TypeEncoder, self).default(obj)


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='MSM数値予報モデルとラジオゾンデによる観測風との誤差統計確率楕円を求めるスクリプト'
    )

    parser.add_argument('place')
    parser.add_argument('year_range')
    parser.add_argument('month_range')
    parser.add_argument('day_range')
    parser.add_argument('init_time')
    parser.add_argument('forecast_time')

    parser.add_argument('--rawin_hour', default=9)

    args = parser.parse_args()

    year_range = [int(y) for y in args.year_range.split(':')]
    month_range = [int(m) for m in args.month_range.split(':')]
    day_range = [int(d) for d in args.day_range.split(':')]
    init_time = datetime.timedelta(hours=int(args.init_time))
    forecast_time = datetime.timedelta(hours=int(args.forecast_time))
    place = args.place

    rawin_hour = int(args.rawin_hour)

    years = getRange(year_range)
    months = getRange(month_range)
    days = getRange(day_range)

    alt_min = 200
    alt_max = 7100
    alt_step = 150
    alt_axis = np.arange(alt_min, alt_max+alt_step, alt_step)
    n_alt = len(alt_axis)

    target_hour = int((init_time + forecast_time).seconds / 3600)
    fore2target_hour = int(args.forecast_time)

    wind_error = [np.zeros((0, 4))] * n_alt
    for y in years:
        for m in months:
            for d in days:
                this_date = datetime.datetime(y, m, d, target_hour)
                rawin_date = datetime.datetime(y, m, d, rawin_hour)
                print('-------------------')
                print(this_date)
                forecast_datetime = this_date - forecast_time
                print('forecast_date:', forecast_datetime)

                msmwin, msm_alt = getMSMWind(place, forecast_datetime, fore2target_hour, interp_kind='linear')
                if msmwin is None:
                    print('Cannot get MSM Wind')
                    continue
                msm_alt_min = np.min(msm_alt)

                rawin, rawin_alt = getRawin(place, rawin_date, interp_kind='linear')
                if rawin is None:
                    print('Cannot get Rawin')
                    continue
                rawin_alt_min = np.min(rawin_alt)

                for i, alt in enumerate(alt_axis):
                    if msm_alt_min > alt or rawin_alt_min > alt:
                        continue

                    rawin_tmp = rawin(alt)
                    error = np.array(rawin_tmp - msmwin(alt))
                    wind_error_tmp = np.concatenate((error, rawin_tmp))
                    wind_error[i] = np.append(
                        wind_error[i],
                        wind_error_tmp[None, :],
                        axis=0
                        )

    print('wind_error', np.shape(wind_error))

    stat_parameters = {}

    stat_parameters['alt_axis'] = alt_axis

    stat_parameters['years'] = years
    stat_parameters['months'] = months
    stat_parameters['days'] = days
    stat_parameters['location'] = place
    stat_parameters['target_hour'] = int(target_hour)
    stat_parameters['MSM_init_hour'] = int(args.init_time)
    stat_parameters['MSM_forecast_hour'] = int(args.forecast_time)

    ######################################
    # 統計量の計算
    ######################################
    mu4 = []
    sigma4 = []
    for wind in wind_error:
        # 4変量の平均と共分散行列
        mu4_tmp, sigma4_tmp = getStatParameters(wind)
        mu4.append(mu4_tmp)
        sigma4.append(sigma4_tmp)

    stat_parameters['mu4'] = mu4
    stat_parameters['sigma4'] = sigma4

    out_foldername = './outputs/'
    out_filename = 'error_stat_JST{:0>2}+{}h.json'.format(args.init_time, args.forecast_time)
    out_path = os.path.join(out_foldername, out_filename)
    if not os.path.exists(out_foldername):
        os.makedirs(out_foldername)

    with open(out_path, 'w') as f:
        json.dump(stat_parameters, f, indent=4, cls=TypeEncoder)
    