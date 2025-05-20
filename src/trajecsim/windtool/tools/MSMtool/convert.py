#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 01:27:20 2018

@author: shugo
"""
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
from scipy import interpolate
#from mpl_toolkits.mplot3d import Axes3D


def _convert(df,dfConverted,m):      #m = 1から16まで
    nrow = 60973    #格子点数（気圧面データのやつ）地上データは格子点数がことなるので注意
    if m>13:
        n =6*12+1+(m-13)*5 
    else:
        n = 6*(m-1)+1
    #HGT
    df_tmp = df.loc[nrow*(n-1):nrow*n-1,[0,1,4,5,3,6]].reset_index(drop = True)       #カラム名は抜き出した元のものが引き継がれる
    dfConverted["date1"] =  df_tmp[0] # inital date of MSM model        #なのでここで指定するインデックスは注意0，1，4，5，3，6の順だよ
    dfConverted["date2"] =  df_tmp[1] # forecasted time in this file
    dfConverted["log"] =  df_tmp[4]   # longtitute
    dfConverted["lat"] =  df_tmp[5]   # altitude
    dfConverted["hPa"] =  df_tmp[3]   # pressure
    dfConverted["HGT"] =  df_tmp[6]   # altitude 
    #print(m,"HGT")
    #UGRD: vel. in x-direction (EW)
    df_tmp = df.loc[nrow*n:nrow*(n+1)-1,[6]]
    dfConverted["UGRD"] = df_tmp.reset_index(drop = True)[6]      #reset_index()でインデックスを振り直している（そのままだとindexはnrow～nrow*2-1となる）そのままだと代入先にそんなindexないよって怒られる
    #print(df_tmp)
    #VGRD: vel in y-direction (NS)
    df_tmp = df.loc[nrow*(n+1):nrow*(n+2)-1,[6]]
    dfConverted["VGRD"] = df_tmp.reset_index(drop = True)[6]

    #TMP: temperature
    df_tmp = df.loc[nrow*(n+2):nrow*(n+3)-1,[6]]
    dfConverted["TMP"] = df_tmp.reset_index(drop = True)[6]

    #VVEL: vertical vel. 
    df_tmp = df.loc[nrow*(n+3):nrow*(n+4)-1,[6]]
    dfConverted["VVEL"] = df_tmp.reset_index(drop = True)[6]
    
    del df_tmp
    return None

def convert_csv(csv_tmp_name, csv_output_filename):
    # --------------------------
    # convert wgrib2 raw output csv into better-formatted csv.
    # input: 
    # csv_tmp_name = csv file converted from. raw output of wgrib2
    # csv_output_filename = csv file converted to. 
    # --------------------------
    
    # convert tmp_csv to another csv
    df = pd.read_csv(csv_tmp_name,delimiter = ',',header=None,skiprows = 0,engine='python', error_bad_lines=False, encoding = "Shift-JIS")
    
    dfConverted_1000 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_975 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_950 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_925 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_900 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_850 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_800 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_700 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_600 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_500 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_400 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_300 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_250 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_200 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_150 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    dfConverted_100 = pd.DataFrame(columns = ['date1','date2','log','lat','hPa','HGT','UGRD','VGRD','TMP','VVEL'])
    
    #ここから地道にデータを抜いていく
    #気圧面ごとに分けているのは処理を単純化するため。最後に結合してcsvに書き出す
    
    #気圧面No（m）を指定すると整形してくれる便利な関数
    """
    気圧面対応表
    1000hPa　 m=1
    975hPa     2
    950hPa     3
    925hPa     4
    900hPa     5
    850hPa     6
    800hPa     7
    700hPa     8
    600hPa     9
    500hPa     10
    400hPa     11
    300hPa     12
    ##此処から先はいらないかもしれない
    250hPa     13
    200hPa     14
    150hPa     15
    100hPa     16
    """
    
    #データ整形    
    _convert(df,dfConverted_1000,1)
    _convert(df,dfConverted_975,2)
    _convert(df,dfConverted_950,3)
    _convert(df,dfConverted_925,4)
    _convert(df,dfConverted_900,5)
    _convert(df,dfConverted_850,6)
    _convert(df,dfConverted_800,7)
    _convert(df,dfConverted_700,8)
    _convert(df,dfConverted_600,9)
    _convert(df,dfConverted_500,10)
    _convert(df,dfConverted_400,11)
    _convert(df,dfConverted_300,12)
    _convert(df,dfConverted_250,13)
    _convert(df,dfConverted_200,14)
    _convert(df,dfConverted_150,15)
    _convert(df,dfConverted_100,16)
    
    df_out = pd.concat([dfConverted_1000,dfConverted_975,dfConverted_950,dfConverted_925,dfConverted_900,dfConverted_850,\
               dfConverted_800,dfConverted_700,dfConverted_600,dfConverted_500,dfConverted_400,dfConverted_300,\
               dfConverted_250,dfConverted_200,dfConverted_150,dfConverted_100],ignore_index = True) #これで後方に連結できる
    df_out.to_csv(csv_output_filename,index = False)
    del df
    del dfConverted_1000
    del dfConverted_975
    del dfConverted_950
    del dfConverted_925
    del dfConverted_900
    del dfConverted_850
    del dfConverted_800
    del dfConverted_700
    del dfConverted_600
    del dfConverted_500
    del dfConverted_400
    del dfConverted_300
    del dfConverted_250
    del dfConverted_200
    del dfConverted_100
    del df_out
    
def interpolate_space(forecast_csv_filename, interp_output_filename, point_coord, plot_flag=False):
    # -------------------------------
    # spacial interpolation of grid forecast (MSM) data.
    # returns altitude vs wind speed/direc at a point of interest.
    # input: 
    # forecast_csv_filename = csv contatins MSM data. converted format generated by "convert_csv"
    # point_coord = [lat,log] : coordinate of point of interest. typically launch site
    # -------------------------------
    
    # max distance[m] to be used from the point of interest. 
    # i.e., data where distance<max_distance will be used
    max_distance = 30000.
    max_altitude = 10000.
    
    # -----------------------
    
    # -----------------------
    # import
    # -----------------------
    # latitude to meter conversion
    lat2meter = 2* np.pi * 6378150 / 360
    # longtitude to meter 
    log2meter = 2* np.pi * 6378150 * np.cos(point_coord[0]*np.pi/180) / 360
    
    # NOTE: in prediction data, points are in every 0.125deg longtitude and 0.1deg latitude (~10km)
    
    # import data into DataFrame
    df = pd.read_csv(forecast_csv_filename)
    # extract info at where +-1deg(100km) from the point of interest
    df = df[df['lat'] <= point_coord[0]+0.3]
    df = df[df['lat'] >= point_coord[0]-0.3]
    df = df[df['log'] <= point_coord[1]+0.3]
    df = df[df['log'] >= point_coord[1]-0.3]
    
    # output reduced data
    # df.to_csv('2017082000+9hour_converted_reduced.csv', index=False)
    
    # -----------------------
    # extract data points to be used
    # -----------------------
    # compute distance [m] from the point of interest
    df['distance'] = ( (( df['lat']-point_coord[0])*lat2meter) **2. + ((df['log']-point_coord[1])*log2meter) **2. ) **0.5
    
    # cut off points whose disrance > max_distance
    # df = df[df['distance'] < max_distance]
    
    # -----------------------
    # weighted average
    # -----------------------
    # weighted average, i.e., nearer the distance, more important the point is
    #df['weight'] = 1. / df['distance'] * 10e4
    
    # weighted average
    # get weighted values
    #df['HGT_w']  = df['HGT']  * df['weight']
    #df['UGRD_w'] = df['UGRD'] * df['weight']
    #df['VGRD_w'] = df['VGRD'] * df['weight']
    #df['VVEL_w'] = df['VVEL'] * df['weight']
    #df['TMP_w']  = df['TMP']  * df['weight']
    
    hPa_all = np.array([1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100])
    
    # arrays for averaged values at the point of interest
    #altitude_avg = np.zeros(len(hPa_all))
    #wind_vec_avg = np.zeros((len(hPa_all), 3))
    #temprature_avg = np.zeros(len(hPa_all))
    
    # arrays for interpolated values at the point of interest
    altitude_interp = np.zeros(len(hPa_all))
    wind_vec_interp = np.zeros((len(hPa_all), 3))
    temprature_interp = np.zeros(len(hPa_all))
    
    # arrays for all the grids raw data
    n_grid = len(df[df['hPa'] == '1000 mb'].index)
    alt_all = np.zeros( (n_grid, len(hPa_all) ) ) #(N_point * N_alt)
    wind_all = np.zeros( (n_grid, len(hPa_all), 3 ) ) #(N_point * N_alt * xyz)
    tmp_all = np.zeros( (n_grid, len(hPa_all) ) ) #(N_point * N_alt)
    
    
    # loop over hPa
    for i in range(len(hPa_all)):
        # hPa name
        hPa_name = str(hPa_all[i]) + ' mb'
        df_tmp = df[df['hPa'] == hPa_name]
        
        latitude_tmp = np.array( df_tmp['lat'].drop_duplicates() )
        longtitude_tmp = np.array( df_tmp['log'].drop_duplicates() )
        
        # """
        # ---------------------
        #  altitude interpolation
        altitude_tmp = np.array( df_tmp['HGT'] ).reshape(len(latitude_tmp), len(longtitude_tmp))
        func_HGT = interpolate.RectBivariateSpline( latitude_tmp,longtitude_tmp,altitude_tmp)
        
        # ---------------------
        # UGRD interpolation
        UGRD_tmp = np.array(df_tmp['UGRD']).reshape(len(latitude_tmp), len(longtitude_tmp))
        func_UGRD = interpolate.RectBivariateSpline( latitude_tmp,longtitude_tmp,UGRD_tmp)
        # UGRD_itp = func(point_coord[0], point_coord[1])
        
        # ---------------------
        # VGRD interpolation
        VGRD_tmp = np.array(df_tmp['VGRD']).reshape(len(latitude_tmp), len(longtitude_tmp))
        func_VGRD = interpolate.RectBivariateSpline( latitude_tmp,longtitude_tmp,VGRD_tmp)
        # VGRD_inp = func(point_coord[0], point_coord[1])
        
        # ---------------------
        # VVEL interpolation
        VVEL_tmp = np.array(df_tmp['VVEL']).reshape(len(latitude_tmp), len(longtitude_tmp))
        func_VVEL = interpolate.RectBivariateSpline( latitude_tmp,longtitude_tmp,VVEL_tmp)
        
        #------------------
        # TMP interpolation
        TMP_tmp = np.array( df_tmp['TMP'] ).reshape(len(latitude_tmp), len(longtitude_tmp))
        func_TMP = interpolate.RectBivariateSpline( latitude_tmp,longtitude_tmp,TMP_tmp) 
        
        # altitude array
        altitude_interp[i] = func_HGT(point_coord[0], point_coord[1])
        # wind vector array
        wind_vec_interp[i,:] = np.array( [ func_UGRD(point_coord[0], point_coord[1])[0,0], func_VGRD(point_coord[0], point_coord[1])[0,0], func_VVEL(point_coord[0], point_coord[1])[0,0] ])
        # temperature array
        temprature_interp[i] = func_TMP(point_coord[0], point_coord[1])
        
        
        # --------------------
        #  get raw data
        # --------------------
        # loop over grid points
        alt_all[:,i] = df_tmp.iloc[:,5]
        wind_all[:,i,0] = df_tmp.iloc[:,6]
        wind_all[:,i,1] = df_tmp.iloc[:,7]
        wind_all[:,i,2] = df_tmp.iloc[:,9]
        tmp_all[:,i] = df_tmp.iloc[:,8]
        
        
    wind_speed_interp = np.linalg.norm(wind_vec_interp, axis = 1)
        
    #print('distance used[km]: ',  max_distance / 1000)
    #print('number of grids used: ', n_grid)
    
    df_interp = pd.DataFrame( {'altitude': pd.Series(altitude_interp), 
                               'wind_u': pd.Series(wind_vec_interp[:,0]),
                               'wind_v': pd.Series(wind_vec_interp[:,1]),
                               'wind_w': pd.Series(wind_vec_interp[:,2]), 
                               'wind_speed': pd.Series(wind_speed_interp), 
                               'temperature':pd.Series(temprature_interp) })
    df_interp.to_csv(interp_output_filename, index=False)
    
    '''
    if plot_flag:
        # --------------------
        #  plot averaged
        # --------------------
        
        indices = altitude_interp < max_altitude
        wind_vec_interp = wind_vec_interp[indices, :]
        altitude_interp = altitude_interp[indices]
        temprature_interp = temprature_interp[indices]
        wind_all = wind_all[:,indices,:]
        tmp_all = tmp_all[:,indices]
        alt_all = alt_all[:,indices]
        
        plt.figure(1)
        #plt.plot(-wind_vec_avg[:,0], altitude_avg/1000, 'o', label='AVG: west to east')
        #plt.plot(wind_vec_avg[:,1], altitude_avg/1000, 'o', label='AVG: south to north')
        plt.plot(wind_vec_interp[:,0], altitude_interp/1000, label='from west')
        plt.plot(wind_vec_interp[:,1], altitude_interp/1000, label='from south')
        # plt.plot(wind_speed_interp[:], altitude_interp/1000, label='INTERP: speed')
        plt.title('Wind speed profile at the point')
        plt.xlabel('wind speed [m/s]')
        plt.ylabel('altitude [km]')
        plt.legend()
        plt.grid()
        
        plt.figure(2)
        #plt.plot(temprature_avg, altitude_avg/1000, 'o', label='AVG')
        plt.plot(temprature_interp, altitude_interp/1000)
        plt.title('Temperature profile at the point')
        plt.xlabel('temperature [K]')
        plt.ylabel('altitude [km]')
        # plt.legend()
        plt.grid()
        
        # --------------------
        #  plot all
        # --------------------
        for i in range(n_grid):
            # east to west
            plt.figure(3)
            plt.plot(wind_all[i,:,0], alt_all[i,:]/1000)
            # south to north
            plt.figure(4)
            plt.plot(wind_all[i,:,1], alt_all[i,:]/1000)
            
            plt.figure(5)
            plt.plot(tmp_all[i,:], alt_all[i,:]/1000)
            
        plt.figure(3)
        plt.title('west-to-east wind dist. near the point')
        plt.xlabel('wind speed [m/s]')
        plt.ylabel('altitude [km]')
        plt.grid()
        
        plt.figure(4)
        plt.title('south-to-north wind dist. near the point')
        plt.xlabel('wind speed [m/s]')
        plt.ylabel('altitude [km]')
        plt.grid()
        
        plt.figure(5)
        plt.title('temperature dist. near the point')
        plt.xlabel('temperature [K]')
        plt.ylabel('altitude [km]')
        plt.grid()
    # END IF
    '''
    return