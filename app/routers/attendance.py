from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.models.student import Student
from app.services.grade_calculator import get_attendance_summary
from app.templates_config import templates

router = APIRouter()


@router.get("/student/{student_id}", response_class=HTMLResponse)
async def get_attendance(
    student_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """出席状況（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"
    summary = get_attendance_summary(db, student_id)
    return templates.TemplateResponse(
        "partials/attendance.html",
        {"request": request, "summary": summary},
    )
