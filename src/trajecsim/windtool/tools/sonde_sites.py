import pandas as pd
import numpy as np
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen


# 観測所名が半角の方がいいのでENGLISH版ページを採用
sonde_sites_url = 'https://www.jma.go.jp/jma/en/Activities/upper/upper.html'

this_file_path = os.path.abspath(os.path.dirname(__file__))
sonde_sites_csv_path = os.path.join(this_file_path, 'sonde_sites.csv')

def degminstr2decimals(degstr:str):
    deg_minute = degstr.split('°')
    deg_minute[1] = deg_minute[1].split('′')[0]
    degrees = int(deg_minute[0])
    minutes = float(deg_minute[1])
    return degrees + minutes/60.0

def updateSondeSitesList():
    # BeautifulSoupを使って表の部分のHTMLを抜き出し
    # ENGLISHページは表の形式が特殊になっていてBeutifulSoupを使用しタグを指定する必要あり
    # html5lib, lxmlなどの外部ライブラリが必要
    html = urlopen(sonde_sites_url)
    soup = BeautifulSoup(html, features="lxml")
    tbody_ = soup.find_all('tbody')[1]
    table = tbody_.tbody
    table = table.wrap(soup.new_tag("table"))

    df = pd.io.html.read_html(str(table), header=0)
    df = df[0]
    
    df = df.rename(columns = {
        'Region ID':'region_id',
        'Station':'station_name',
        'Location':'location',
        'Latitude(degree)':'latitude',
        'Longitude(degree)':'longitude'
    })

    latitudes_str = df['latitude']
    longitudes_str = df['longitude']
    latitude = [degminstr2decimals(lat) for lat in latitudes_str]
    longitude = [degminstr2decimals(lon) for lon in longitudes_str]
    df['latitude'] = latitude
    df['longitude'] = longitude
    df.to_csv(sonde_sites_csv_path)
    return df

def getSondeSitesList():
    if os.path.exists(sonde_sites_csv_path):
        df = pd.read_csv(sonde_sites_csv_path, index_col=0)
        return df
    else:
        print('sonde_sites.csv was not found. Trying to collect the list from "'+sonde_sites_url+'".')
        return updateSondeSitesList()

sonde_df = getSondeSitesList()

def getSondeLocation(station_name:str):
    df = sonde_df.loc[sonde_df['station_name'] == station_name]
    if df is None:
        raise ValueError('the station name'+station_name+'was not found.')
    return np.array([float(df['latitude']), float(df['longitude'])])

def getRegionID(station_name):
    df = sonde_df.loc[sonde_df['station_name'] == station_name]
    return int(df['region_id'])

if __name__ == '__main__':
    print('Updating radiosonde sites list...')
    loc = updateSondeSitesList()
    print('completed.')
    print(loc)
