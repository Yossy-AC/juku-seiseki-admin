# クイックスタートガイド

塾成績管理システム（FastAPI + HTMX）をローカルで実行するための手順です。

## 動作確認済み環境

- Python 3.12+
- Windows 10/11（Bash / WSL / Git Bash推奨）

## 1. 初期設定（初回のみ）

```bash
# リポジトリをクローン
cd Student-Manager

# 環境ファイルを作成
cp .env.example .env

# 依存関係をインストール
pip install fastapi uvicorn[standard] sqlalchemy jinja2 python-multipart \
            itsdangerous python-dotenv passlib[bcrypt] starlette
```

## 2. データベース初期化（初回のみ）

既存の JSON データを SQLite に移行：

```bash
PYTHONIOENCODING=utf-8 python scripts/import_json.py
```

出力例：
```
✓ 高3英語@難関大
✓ 田中太郎
✓ 成績ID: g001
✓ 出席ID: a001
✅ データ移行が完了しました
```

## 3. 開発サーバー起動

### 方法 A: Windows バッチファイル（推奨）

```bash
# Windows コマンドプロンプトで実行
run.bat
```

このバッチファイルは以下を自動で行います：
- 古いプロセスを終了
- UTF-8 エンコーディング設定
- サーバー起動

### 方法 B: Python スクリプト

```bash
python run.py
```

### 方法 C: 直接コマンド実行

```bash
cd /c/GitHub_StudentManager/Student-Manager
PYTHONIOENCODING=utf-8 uvicorn app.main:app --port 8000
```

**注意**: Windows では `--reload` フラグを使用するとエラーが発生する場合があります。その場合は上記の方法 A または B を使用してください。

出力例：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## 4. ブラウザでアクセス

| ページ | URL |
|--------|-----|
| ログイン画面 | http://localhost:8000/login |
| 管理画面（要ログイン） | http://localhost:8000/admin |
| ヘルスチェック | http://localhost:8000/health |

## 5. ログイン

**デフォルトパスワード**（.env に記載）:
```
ADMIN_PASSWORD=your-admin-password-here
```

## トラブルシューティング

### PermissionError: [WinError 5] アクセスが拒否されました

**原因**: Windows での multiprocessing の問題

**解決策**: 以下の方法で起動してください

```bash
# 方法 1: バッチファイル使用（推奨）
run.bat

# 方法 2: Python スクリプト使用
python run.py

# 方法 3: --reload なしで実行
python -m uvicorn app.main:app --port 8000
```

### ポート 8000 が使用中

```bash
# 別のポート使用
python -m uvicorn app.main:app --port 8001
```

### Unicode エラー

```bash
# UTF-8 エンコーディング指定（必須）
PYTHONIOENCODING=utf-8 python scripts/import_json.py
```

### 404 エラー（{"detail":"Not Found"}）

- ブラウザキャッシュをクリア（Ctrl+Shift+Delete）
- サーバーを再起動
- 正しいポート（デフォルト 8000）でアクセス

## エンドポイント確認

```bash
python << 'EOF'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.get("/health")
print(response.json())  # {'status': 'ok'}
EOF
```

## 開発時便利なコマンド

```bash
# コード修正時の自動リロード
uvicorn app.main:app --reload

# ログレベル設定
uvicorn app.main:app --log-level debug

# バインドアドレス指定
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 本番環境デプロイ

詳細は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

```bash
# Railway へのデプロイ
git push origin main
# Railway ダッシュボードで自動デプロイ
```

## 次のステップ

1. **ローカル開発**
   - `/admin` タブで生徒・成績データを管理
   - `/upload` で CSV ファイルをインポート
   - `/dashboard/s001` で生徒ダッシュボードを確認

2. **Rails へのデプロイ**
   - [DEPLOYMENT.md](DEPLOYMENT.md) の手順に従う
   - 環境変数を設定（SECRET_KEY, ADMIN_PASSWORD, DATABASE_URL）
   - PostgreSQL プラグインを追加（本番環境推奨）

3. **カスタマイズ**
   - テンプレート編集: `app/templates/`
   - ビジネスロジック: `app/services/`
   - ルート設定: `app/routers/`
