from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from app.database import create_db_and_tables
from app.config import settings
from app.routers import pages, students, grades, classes, attendance, upload, auth as auth_router

# FastAPI アプリ作成
app = FastAPI(
    title="塾成績管理システム",
    version="0.1.0"
)

# セッションミドルウェア設定
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# 静的ファイル配信
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ルーター登録（認証関連は最初に）
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(pages.router, tags=["pages"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(grades.router, prefix="/api/grades", tags=["grades"])
app.include_router(classes.router, prefix="/api/classes", tags=["classes"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])

# アプリ起動時にDBテーブルを作成
create_db_and_tables()

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}
