"""
FastAPI 依存関数
"""

from fastapi import Depends, HTTPException, status, Request


async def require_auth(request: Request):
    """
    認証チェック依存関数

    セッションに authenticated フラグがなければ401エラー
    """
    if not request.session.get("authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True
