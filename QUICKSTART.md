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

```bash
cd /c/GitHub_StudentManager/Student-Manager
PYTHONIOENCODING=utf-8 uvicorn app.main:app --reload --port 8000
```

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

### ポート 8000 が使用中

```bash
# 別のポート使用
PYTHONIOENCODING=utf-8 uvicorn app.main:app --reload --port 8001
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
