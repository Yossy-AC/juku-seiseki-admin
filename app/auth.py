"""
セッション認証ヘルパー
パスワード検証とセッション管理
"""

import hmac
from app.config import settings


def authenticate_admin(password: str) -> bool:
    """
    管理画面用パスワード認証
    hmac.compare_digest でタイミング攻撃を防ぐ
    """
    return hmac.compare_digest(password, settings.ADMIN_PASSWORD)


def clear_session(session: dict):
    """セッションをクリア"""
    session.clear()
