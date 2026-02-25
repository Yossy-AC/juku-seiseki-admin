#!/usr/bin/env python3
"""
開発サーバー起動スクリプト（Windows 対応）
multiprocessing の問題を回避するために使用
"""

import os
import sys
import uvicorn

# 必須の環境変数設定
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app"],  # app ディレクトリの変更を監視
        log_level="info"
    )
