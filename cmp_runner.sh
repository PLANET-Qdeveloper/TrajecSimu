#!/bin/bash

# 1つ目のコマンド
/Users/genta/TrajecSimu/.venv/bin/python /Users/genta/TrajecSimu/src/main.py --output_dir data/78_263 --config_file_path data/input/78_263.yaml

# 2つ目のコマンド
/Users/genta/TrajecSimu/.venv/bin/python /Users/genta/TrajecSimu/src/main.py --output_dir data/82_263 --config_file_path data/input/82_263.yaml

# 3つ目のコマンド
/Users/genta/TrajecSimu/.venv/bin/python /Users/genta/TrajecSimu/src/main.py --output_dir data/78_303 --config_file_path data/input/78_303.yaml

# 4つ目のコマンド
/Users/genta/TrajecSimu/.venv/bin/python /Users/genta/TrajecSimu/src/main.py --output_dir data/82_303 --config_file_path data/input/82_303.yaml

echo "すべての処理が完了しました。"