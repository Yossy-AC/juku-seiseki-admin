from fastapi import HTTPException, status, Request


def is_authenticated(request: Request) -> bool:
    """セッション認証状態を返す（共通ヘルパー）"""
    return request.session.get("authenticated", False)


async def require_auth(request: Request):
    """
    API用 認証依存関数（未認証は401）
    ページルーターは is_authenticated を直接使い、302リダイレクトを返す
    """
    if not is_authenticated(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です",
        )
    return True
