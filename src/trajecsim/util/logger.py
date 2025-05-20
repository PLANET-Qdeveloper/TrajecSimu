import logging
from os import PathLike
from pathlib import Path
from typing import Any

from tqdm import tqdm

PROJECT_NAME = "trajecsim"


class TqdmLoggingHandler(logging.Handler):
    """tqdmと互換性のあるロギングハンドラ"""

    def __init__(self, level=logging.INFO):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging(log_file: PathLike[Any] | str) -> logging.Logger:
    """ルートロガーの設定。他のすべてのロガーに設定が伝搬する"""

    log_file = Path(log_file)
    # ルートロガーを取得
    logger = logging.getLogger(PROJECT_NAME)
    logger.setLevel(logging.INFO)

    # すでに存在するハンドラを削除（重複を防止）
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # フォーマッタの作成
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # tqdmハンドラをコンソール出力用に追加
    tqdm_handler = TqdmLoggingHandler()
    tqdm_handler.setFormatter(formatter)
    logger.addHandler(tqdm_handler)

    # ファイルハンドラ（必要な場合）
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
