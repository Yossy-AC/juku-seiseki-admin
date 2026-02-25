from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# テンプレートディレクトリ設定
templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=templates_dir)

def require_auth_check(request: Request) -> bool:
    """セッション認証チェック"""
    return request.session.get("authenticated", False)

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """ルートページ: ログイン状態により振り分け"""
    if require_auth_check(request):
        return RedirectResponse(url="/admin", status_code=302)
    else:
        return RedirectResponse(url="/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """ログイン画面"""
    # 既にログイン済みなら管理画面へリダイレクト
    if require_auth_check(request):
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """管理画面（ダッシュボードタブを初期表示）"""
    if not require_auth_check(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("admin/index.html", {"request": request})

@router.get("/dashboard/{student_id}", response_class=HTMLResponse)
async def dashboard_page(request: Request, student_id: str):
    """生徒ダッシュボード"""
    if not require_auth_check(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "dashboard/index.html",
        {"request": request, "student_id": student_id}
    )

@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """CSVアップロード画面"""
    if not require_auth_check(request):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("upload/index.html", {"request": request})

@router.get("/admin/tabs/{tab_name}", response_class=HTMLResponse)
async def admin_tab(request: Request, tab_name: str):
    """管理画面タブコンテンツ切り替え（HTMX用）"""
    if not require_auth_check(request):
        return RedirectResponse(url="/login", status_code=302)

    tab_templates = {
        "dashboard": "admin/_dashboard_tab.html",
        "grades": "admin/_grades_tab.html",
        "students": "admin/_students_tab.html",
        "classes": "admin/_classes_tab.html",
        "upload": "upload/index.html",
        "reports": "admin/_reports_tab.html",
    }

    template_path = tab_templates.get(tab_name, "admin/_dashboard_tab.html")
    return templates.TemplateResponse(template_path, {"request": request})
