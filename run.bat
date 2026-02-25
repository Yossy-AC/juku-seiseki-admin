@echo off
REM Windows 用開発サーバー起動スクリプト
REM このスクリプトで multiprocessing の問題を回避できます

cd /d %~dp0

echo ========================================
echo  塾成績管理システム 開発サーバー
echo ========================================
echo.
echo 環境設定中...

REM 古いプロセスを終了
taskkill /IM python.exe /F 2>nul

timeout /t 2 /nobreak

echo サーバーを起動しています...
echo.

REM UTF-8 エンコーディング設定
set PYTHONIOENCODING=utf-8

REM サーバー起動
python run.py

pause
