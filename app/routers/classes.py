from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.models.class_ import Class
from app.models.student import Student
from app.templates_config import templates

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def list_classes(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """講座一覧（HTMX用）"""
    classes = db.query(Class).all()
    return templates.TemplateResponse(
        "partials/classes_table.html",
        {"request": request, "classes": classes},
    )


@router.get("/{class_id}/students", response_class=HTMLResponse)
async def get_class_students(
    class_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """講座別生徒セレクトボックス（HTMX用、連鎖セレクト）"""
    students = db.query(Student).filter(Student.class_id == class_id).all()
    return templates.TemplateResponse(
        "partials/class_students_select.html",
        {"request": request, "students": students},
    )
