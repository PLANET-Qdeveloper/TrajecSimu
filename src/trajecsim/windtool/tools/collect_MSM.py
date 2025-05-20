import argparse
import os
import subprocess

import numpy as np
from MSMtool.download_MSM import downloadMSM
from MSMtool.interpolater import interpolateMSM

# from download_MSM import downloadMSM
from MSMtool.MSM2csv import MSM2csv


def getRange(range_array):
    if len(range_array) == 3:
        array = np.arange(range_array[0], range_array[1] + 1, range_array[2])
    elif len(range_array) == 2:
        array = np.arange(range_array[0], range_array[1] + 1)
    elif len(range_array) == 1:
        array = np.array([range_array[0]])
    else:
        array = np.array([])
    return array


if __name__ == "__main__":
    this_file_path = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(
        description="指定した地点のMSM数値予報モデルの風向風速データを取得しcsvに変換するツール"
    )
    parser.add_argument(
        "place",
        help='風向風速を取りだす地点名。現在はラジオゾンデの観測所名に加え各海打ち射点"Izu-umi","Noshiro-umi"から指定可能。',
    )
    parser.add_argument("year_range")
    parser.add_argument("month_range")
    parser.add_argument("day_range")
    parser.add_argument("init_time")
    parser.add_argument("forecast_time")

    parser.add_argument("--wgrib2_exec_path", default="wgrib2", help='Exec path of wgrib2. default:"wgrib2"')

    args = parser.parse_args()

    year_range = [int(y) for y in args.year_range.split(":")]
    month_range = [int(m) for m in args.month_range.split(":")]
    day_range = [int(d) for d in args.day_range.split(":")]
    init_time_range = [int(h) for h in args.init_time.split(":")]
    forecast_time_range = [int(f) for f in args.forecast_time.split(":")]
    print(year_range, month_range, day_range, init_time_range, forecast_time_range)

    years = getRange(year_range)
    months = getRange(month_range)
    days = getRange(day_range)
    init_times = getRange(init_time_range)
    fore_times = getRange(forecast_time_range)

    interp_place = args.place

    # loop over years
    for y in years:
        # loop over monthes
        for m in months:
            # loop over days
            for d in days:
                date_str = "{yyyy}{mm:02}{dd:02}".format(yyyy=y, mm=m, dd=d)
                for h in init_times:
                    for f in fore_times:
                        bin_output_dir = os.path.join(this_file_path, "MSMtool/bin/JST" + str(h) + "+" + str(f) + "h/")
                        rawcsv_output_dir = os.path.join(
                            this_file_path, "MSMtool/csv/JST" + str(h) + "+" + str(f) + "h/"
                        )
                        interp_csv_output_dir = os.path.join(
                            this_file_path, "../wind_MSM/" + interp_place + "/JST" + str(h) + "+" + str(f) + "h/"
                        )
                        downloadMSM(y, m, d, h, f, bin_output_dir)
                        MSM2csv(y, m, d, h, f, rawcsv_output_dir, args.wgrib2_exec_path)
                        interpolateMSM(y, m, d, h, f, interp_place, interp_csv_output_dir)
