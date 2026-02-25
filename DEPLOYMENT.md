# Railway へのデプロイ方法

このドキュメントは、塾成績管理システム（FastAPI + HTMX）を Railway にデプロイするための手順です。

## 前提条件

- Railway アカウント（https://railway.app）
- GitHub アカウント
- Git がインストール済み

## デプロイの概要

Railway では以下のファイルが自動的に検出されます：
- `Dockerfile` - コンテナイメージをビルド
- `railway.toml` - Railway 固有の設定
- `pyproject.toml` - Python 依存関係

## ステップバイステップガイド

### 1. GitHub にコードをプッシュ

```bash
git push origin main
```

### 2. Railway にログイン

https://railway.app にアクセスしてログインします。

### 3. 新しいプロジェクトを作成

1. Railway ダッシュボードで「+ New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. GitHub リポジトリを認可・選択

### 4. 環境変数を設定

Railway プロジェクトの「Variables」タブで以下を設定：

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `SECRET_KEY` | セッション暗号化キー（32文字以上） | `your-random-secret-key-here` |
| `ADMIN_PASSWORD` | 管理画面ログインパスワード | `secure-password-here` |
| `DATABASE_URL` | PostgreSQL接続文字列 | `postgresql://user:pass@host:5432/db` |
| `DEBUG` | デバッグモード | `false` |

**SECRET_KEY の生成例：**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 5. Railway PostgreSQL プラグイン追加（推奨）

本番環境ではSQLiteではなくPostgreSQLを使用します：

1. プロジェクトで「+ Add」をクリック
2. 「Database」から「PostgreSQL」を選択
3. Railway が自動的に接続情報を環境変数に追加します（`DATABASE_URL`）

### 6. デプロイを確認

1. Railway がビルド・デプロイを自動実行します
2. 「Deployments」タブで進行状況を確認
3. ログに問題がないか確認

### 7. アプリケーションにアクセス

- Railway が自動的にドメインを割り当てます（例：`your-app-xyz.railway.app`）
- ログイン画面: `https://your-app-xyz.railway.app/login`
- 管理画面: `https://your-app-xyz.railway.app/admin`

## トラブルシューティング

### ビルドエラー

**`uv: command not found`**
- Dockerfile が正しく uv をインストールしているか確認
- `python -m pip install uv` の代わりに `pip install uv` を使用

**`ModuleNotFoundError`**
- `uv.lock` ファイルが Git に含まれているか確認
- ローカルで `uv sync` を実行して `uv.lock` を生成

### ランタイムエラー

**`DATABASE_URL not set`**
- Railway Variables タブで `DATABASE_URL` が設定されているか確認
- PostgreSQL プラグインが正しくデプロイされたか確認

**`SECRET_KEY too short`**
- `SECRET_KEY` は最低32文字必要です
- `secrets.token_urlsafe(32)` で生成

### ログの確認

Railway ダッシュボード内の「Logs」タブからリアルタイムログを確認：
```
[INFO] Application startup complete
[INFO] Uvicorn running on 0.0.0.0:8000
```

## 本番環境のベストプラクティス

1. **認証情報の管理**
   - `SECRET_KEY`, `ADMIN_PASSWORD` は強力な値に設定
   - 定期的にパスワードを変更

2. **データベース**
   - SQLite ではなく PostgreSQL を使用
   - 定期的にバックアップを取得

3. **監視とロギング**
   - Railway の監視ツールで CPU/メモリ使用率を監視
   - ログで定期的にエラーをチェック

4. **セキュリティ**
   - HTTPS は Railway が自動的に有効化
   - カスタムドメインを設定する場合は DNS レコード更新後に SSL を有効化

## カスタムドメイン設定

1. Railway プロジェクト > 「Networking」タブ
2. 「+ Add Custom Domain」をクリック
3. ドメイン名を入力（例：`grades.example.com`）
4. DNS プロバイダーで CNAME レコード追加：
   ```
   CNAME: grades.example.com → your-app-xyz.railway.app
   ```

## ローカル開発環境

開発環境では SQLite を使用：

```bash
# 環境変数を設定
cp .env.example .env

# 開発サーバーを起動
uv run uvicorn app.main:app --reload --port 8000
```

## データベーススキーマの自動作成

アプリケーション起動時に以下が自動実行：
- SQLAlchemy がスキーマを作成
- 初期データは `scripts/import_json.py` で移行

```bash
# 既存 JSON データを DB に移行
uv run python scripts/import_json.py
```

## 参考リンク

- [Railway ドキュメント](https://docs.railway.app)
- [FastAPI デプロイガイド](https://fastapi.tiangolo.com/deployment)
- [Uvicorn 設定](https://www.uvicorn.org/settings)
