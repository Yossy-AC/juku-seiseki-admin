import logging
from datetime import date as date_type
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.models.student import Student
from app.templates_config import templates

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def list_students(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """生徒一覧（HTMX用）"""
    students = db.query(Student).order_by(Student.name).all()
    return templates.TemplateResponse(
        "partials/students_table.html",
        {"request": request, "students": students},
    )


@router.post("", response_class=HTMLResponse)
async def create_student(
    request: Request,
    name: str = Form(...),
    name_kana: str = Form(""),
    gender: str = Form(""),
    high_school: str = Form(""),
    target_university: str = Form(""),
    target_dept: str = Form(""),
    class_id: str = Form(""),
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """生徒追加（HTMX用）"""
    try:
        # ID 自動採番（最大の数値 + 1）
        max_id = 0
        for s in db.query(Student).all():
            try:
                num = int(s.id.lstrip("s"))
                if num > max_id:
                    max_id = num
            except ValueError:
                pass
        new_id = f"s{max_id + 1:03d}"

        new_student = Student(
            id=new_id,
            name=name,
            name_kana=name_kana or None,
            gender=gender or None,
            high_school=high_school or None,
            target_university=target_university or None,
            target_dept=target_dept or None,
            class_id=class_id or None,
            join_date=date_type.today(),
        )
        db.add(new_student)
        db.commit()

        students = db.query(Student).order_by(Student.name).all()
        return templates.TemplateResponse(
            "partials/students_table.html",
            {"request": request, "students": students},
        )
    except Exception as e:
        logger.error("Student create error: %s", e, exc_info=True)
        return "<p style='color:#c62828;'>保存中にエラーが発生しました</p>"
