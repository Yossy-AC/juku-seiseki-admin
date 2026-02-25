from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# Phase 3 で実装予定
@router.get("", response_class=HTMLResponse)
async def list_classes():
    """講座一覧（HTMX用）"""
    return "<p>講座一覧は Phase 3 で実装予定</p>"

@router.get("/{class_id}/students", response_class=HTMLResponse)
async def get_class_students(class_id: str):
    """講座別生徒セレクトボックス（HTMX用）"""
    return f"<p>講座 {class_id} の生徒は Phase 3 で実装予定</p>"
