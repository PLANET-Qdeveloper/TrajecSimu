
# StatWindTool

弾道シミュレーションで用いる誤差統計風モデルの誤差統計確率楕円のプロファイルを出力するツール。

MSM数値予報モデルによる予報風ベクトルと、気象庁のラジオゾンデ観測風ベクトルとの差の分布が正規分布に従うと仮定し、
その平均ベクトルと分散共分散行列を導出してjsonデータとして書き出す。

## Features

- 京大生存圏データベースから、指定した日付時刻のMSM数値予報風データをダウンロードし任意地点での風をcsvに書き出すツール `collect_MSM.py`
- 気象庁ラジオゾンデ観測風ページをスクレイピングして指定した日付の観測風データをcsvに書き出すツール `collect_sonde.py`
- 書き出したMSMとラジオゾンデ風から各日の誤差の統計をとり楕円パラメータファイルを書き出すツール `generate_error_ellipse.py`

## Requirements

- python3
- wgrib2

## Dependencies

- BeautifulSoup4
- pandas
- numpy
- scipy

## Usage

### ラジオゾンデ観測所を確認する
[`tools/sonde_sites.csv`](https://github.com/PLANET-Q/StatwindTool/blob/master/tools/sonde_sites.csv) 内の `station_name` 列が利用可能なラジオゾンデ観測所の名前です。
このリストは気象庁ウェブサイトから抽出しており、以下のコマンドを実行することで再度観測所のリストを書き出して更新できます。

```exec_sonde_sites.sh
python tools/sonde_sites.py
```

### ラジオゾンデ観測データをダウンロードしてcsvに書き出す

`tools/collect_sonde.py` でラジオゾンデの観測データをダウンロードし、`wind_Rawin`フォルダ内にcsvとして書き出します。  
以下のように実行すると、秋田観測所の2010~2018年8月1~31日朝9時の観測データを一括でcsvに書き出します。  

- 時刻は 3,9,15,21から選択可能。  
- 観測所名は [`tools/sonde_sites.csv`](https://github.com/PLANET-Q/StatwindTool/blob/master/tools/sonde_sites.csv) 内の `station_name` の名前を指定

```exec_collect_sonde.sh
python tools/collect_sonde.py Akita 2010:2018 8 1:31 9
```

### MSM数値予報データをダウンロードしてcsvに書き出す

まず最初に`wgrib2` をPC上にインストールしておいて、
実行ファイル `wgrib2`(Windowsの場合 `wgrib2.exe`)を
このプロジェクトのフォルダ内にコピーするか、
実行ファイル`wgrib2` のあるディレクトリのパスを後述する
`--wgrib2_exec_path` オプションに指定する必要があります。

以下のように実行すると、ラジオゾンデの秋田観測所と同地点の2010~2018年8月1~31日21時に発表された、9時間後の予報(即ち翌朝6時の予報)風データを一括でcsvに書き出します。  

- 予報発表時刻(初期時刻)は 0時から3時間ごとの時間を指定可能
- 観測所名は ラジオゾンデの観測所名に加え、各海打ち射点"Izu-umi","Noshiro-umi"から指定可能。
- `--wgrib2_exec_path` の後にwgrib2の実行パスを指定します。`wgrib2` の実行ファイルをこのプロジェクトのフォルダ内にコピーした場合は不要です。

```exec_collect_MSM.sh
python tools/collect_MSM.py Akita 2010:2018 8 1:31 21 9 --wgrib2_exec_path "/your/wgrib2/exec/path/wgrib2"
```

### 誤差分散楕円を出す

以下のように実行すると、ラジオゾンデの秋田観測所地点での

- 2010-2018 年 8月1-31 日21時朝9時に観測されたラジオゾンデの観測データ
- 2010-2018 年 8月1-31 日21時に発表された、9時間後の予報(即ち翌朝6時の予報)風データ

との差の統計量をjson形式のファイルに書き出します。
書き出された`json`ファイルは`outputs`フォルダ内に出力されます

```exec_generator.sh
python generate_error_ellipse.py Akita 2010:2018 8 1:31 21 9 --rawin_hour 9
```

## TODO

- ウィンドプロファイラ対応

## LICENSE

MIT
