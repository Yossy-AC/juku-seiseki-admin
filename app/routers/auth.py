from fastapi import APIRouter

router = APIRouter()

# Phase 5 で実装予定
@router.post("/login")
async def login():
    """ログイン（Phase 5 で実装）"""
    return {"message": "ログイン機能は Phase 5 で実装予定"}

@router.post("/logout")
async def logout():
    """ログアウト（Phase 5 で実装）"""
    return {"message": "ログアウト機能は Phase 5 で実装予定"}
