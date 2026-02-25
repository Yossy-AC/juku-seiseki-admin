from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# Phase 2-3 で実装予定
@router.get("", response_class=HTMLResponse)
async def list_students():
    """生徒一覧（HTMX用）"""
    return "<p>生徒一覧は Phase 2-3 で実装予定</p>"

@router.post("", response_class=HTMLResponse)
async def create_student():
    """生徒追加（HTMX用）"""
    return "<p>生徒追加は Phase 2-3 で実装予定</p>"
