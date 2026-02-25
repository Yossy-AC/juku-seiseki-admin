"""
セッション認証ヘルパー
パスワード検証とセッション管理
"""

from passlib.context import CryptContext
from app.config import settings

# パスワードハッシュ化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """パスワードをハッシュ化"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_admin(password: str) -> bool:
    """
    管理画面用パスワード認証

    settings.ADMIN_PASSWORD と比較
    """
    # 環境変数から取得したパスワードと直接比較（簡略版）
    # 本番環境ではハッシュ化されたパスワードと比較すべき
    return password == settings.ADMIN_PASSWORD


def get_session_data(session: dict) -> dict:
    """セッションデータを取得"""
    return {
        "authenticated": session.get("authenticated", False),
        "login_time": session.get("login_time")
    }


def clear_session(session: dict):
    """セッションをクリア"""
    session.clear()
