from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# Phase 4 で実装予定
@router.post("/csv", response_class=HTMLResponse)
async def upload_csv():
    """CSV解析＆プレビュー（HTMX用）"""
    return "<p>CSV解析は Phase 4 で実装予定</p>"

@router.post("/save", response_class=HTMLResponse)
async def save_csv():
    """保存確定（HTMX用）"""
    return "<p>保存確定は Phase 4 で実装予定</p>"

@router.get("/template")
async def download_template():
    """CSVテンプレートダウンロード"""
    return {"message": "CSVテンプレートは Phase 4 で実装予定"}
