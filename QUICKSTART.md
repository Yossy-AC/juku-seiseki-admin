# クイックスタートガイド

塾成績管理システム（FastAPI + HTMX）をローカルで実行するための手順です。

## 動作確認済み環境

- Python 3.12+
- Windows 10/11（Git Bash 推奨）

## 1. 初期設定（初回のみ）

```bash
# リポジトリをクローン後
cd Student-Manager

# 環境ファイルを作成
cp .env.example .env
# .env を編集して SECRET_KEY と ADMIN_PASSWORD を設定

# 依存関係をインストール（uv）
uv sync
```

## 2. データベース初期化（初回のみ）

既存の JSON データを SQLite に移行：

```bash
PYTHONIOENCODING=utf-8 uv run python scripts/import_json.py
```

出力例：
```
✓ 高3英語@難関大
✓ 田中太郎
✓ 成績ID: g001
✓ 出席ID: a001
データ移行が完了しました
```

## 3. 開発サーバー起動

```bash
# 推奨（Windows Git Bash）
python -m uvicorn app.main:app --port 8000

# uv 経由
uv run uvicorn app.main:app --port 8000

# Windows バッチファイル（自動プロセス終了付き）
run.bat
```

**注意**: Windows では `--reload` フラグで multiprocessing エラーが発生する場合があります。上記コマンドはリロードなし起動です。

起動確認：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## 4. ブラウザでアクセス

| ページ | URL |
|--------|-----|
| ログイン画面 | http://localhost:8000/login |
| 管理画面（要ログイン） | http://localhost:8000/admin |
| 生徒ダッシュボード | http://localhost:8000/dashboard/s001 |
| CSVアップロード | http://localhost:8000/upload |
| ヘルスチェック | http://localhost:8000/health |

## 5. ログイン

`.env` に設定した `ADMIN_PASSWORD` でログインしてください。

デフォルト（.env.example）:
```
ADMIN_PASSWORD=your-admin-password-here
```

## トラブルシューティング

### ポート 8000 が使用中

```bash
python -m uvicorn app.main:app --port 8001
```

### uv コマンドが見つからない

```bash
pip install uv
python -m uv sync
```

その後は `python -m uv` を `uv` の代わりに使用してください。

### Unicode エラー（import_json.py）

```bash
PYTHONIOENCODING=utf-8 uv run python scripts/import_json.py
```

### PermissionError: [WinError 5] アクセスが拒否されました

`--reload` を外して起動してください：
```bash
python -m uvicorn app.main:app --port 8000
```

### 404 エラー（{"detail":"Not Found"}）

- ブラウザキャッシュをクリア（Ctrl+Shift+Delete）
- サーバーを再起動
- ポートが合っているか確認

## 開発時便利なコマンド

```bash
# ヘルスチェック確認
curl http://localhost:8000/health

# APIドキュメント確認
# http://localhost:8000/docs （FastAPI 自動生成）

# ログレベル設定
python -m uvicorn app.main:app --log-level debug --port 8000
```

## 本番環境デプロイ

詳細は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

環境変数（Railway ダッシュボードで設定）:
- `SECRET_KEY` - セッション署名用ランダム文字列
- `ADMIN_PASSWORD` - 管理画面ログインパスワード
- `DATABASE_URL` - PostgreSQL URL（Railway が自動設定）

## 主な操作フロー

1. **生徒ダッシュボード**: `/dashboard/s001` → 生徒 ID を変えてアクセス
2. **成績入力**: `/admin` → 成績入力タブ → 講座選択→生徒選択→点数入力
3. **生徒追加**: `/admin` → 生徒管理タブ → 「新規生徒を追加」フォーム展開
4. **CSVインポート**: `/upload` → ファイル選択→プレビュー確認→保存確定
5. **CSVテンプレート**: `/api/upload/template` からダウンロード

## カスタマイズ

- テンプレート編集: [app/templates/](app/templates/)
- ビジネスロジック: [app/services/](app/services/)
- ルート設定: [app/routers/](app/routers/)
- スタイル: [static/css/styles.css](static/css/styles.css)
