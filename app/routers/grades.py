import logging
from datetime import date as date_type
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.models.grade import Grade
from app.models.student import Student
from app.templates_config import templates
from app.services.grade_calculator import (
    get_student_grades,
    calculate_student_average,
    calculate_class_average,
    generate_advice,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def list_grades(
    request: Request,
    limit: int = None,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """最近の成績一覧（管理画面用）"""
    query = db.query(Grade).order_by(Grade.date.desc())
    if limit:
        query = query.limit(limit)
    grades = query.all()
    return templates.TemplateResponse(
        "partials/grades_table.html",
        {"request": request, "grades": grades},
    )


@router.get("/student/{student_id}", response_class=HTMLResponse)
async def get_student_grades_html(
    student_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """生徒別成績テーブル（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"
    grades = get_student_grades(db, student_id)
    return templates.TemplateResponse(
        "partials/grades_table.html",
        {"request": request, "grades": grades},
    )


@router.get("/comparison/{student_id}", response_class=HTMLResponse)
async def get_comparison(
    student_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """クラス平均比較（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"
    student_avg = calculate_student_average(db, student_id)
    class_avg = calculate_class_average(db, student.class_id) if student.class_id else 0
    difference = student_avg - class_avg
    return templates.TemplateResponse(
        "partials/comparison.html",
        {
            "request": request,
            "student_avg": student_avg,
            "class_avg": class_avg,
            "difference": abs(difference),
            "difference_color": "#2e7d32" if difference >= 0 else "#c62828",
            "difference_sign": "+" if difference >= 0 else "-",
        },
    )


@router.get("/advice/{student_id}", response_class=HTMLResponse)
async def get_advice(
    student_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """学習アドバイス（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"
    advice = generate_advice(db, student_id)
    return templates.TemplateResponse(
        "partials/advice.html",
        {"request": request, "advice": advice},
    )


@router.post("", response_class=HTMLResponse)
async def create_grade(
    request: Request,
    student_id: str = Form(...),
    class_id: str = Form(...),
    date: str = Form(...),
    lesson_content: str = Form(""),
    score_comprehension: int = Form(0),
    score_unseen: int = Form(0),
    score_grammar: int = Form(0),
    score_vocabulary: int = Form(0),
    score_listening: int = Form(0),
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """成績入力（HTMX用）"""
    try:
        # lesson_number 自動採番（その生徒の最大 + 1）
        max_lesson = (
            db.query(func.max(Grade.lesson_number))
            .filter(Grade.student_id == student_id)
            .scalar()
        )
        lesson_number = (max_lesson or 0) + 1

        score_total = (
            score_comprehension + score_unseen + score_grammar
            + score_vocabulary + score_listening
        )
        grade_id = f"g_{student_id}_{date}_{lesson_number}"

        new_grade = Grade(
            id=grade_id,
            student_id=student_id,
            class_id=class_id,
            date=date,
            lesson_number=lesson_number,
            lesson_content=lesson_content,
            score_comprehension=score_comprehension,
            score_unseen=score_unseen,
            score_grammar=score_grammar,
            score_vocabulary=score_vocabulary,
            score_listening=score_listening,
            score_total=score_total,
        )
        db.add(new_grade)
        db.commit()

        # 最近5件を返す
        grades = db.query(Grade).order_by(Grade.date.desc()).limit(5).all()
        return templates.TemplateResponse(
            "partials/grades_table.html",
            {"request": request, "grades": grades},
        )
    except Exception as e:
        logger.error("Grade create error: %s", e, exc_info=True)
        return "<p style='color:#c62828;'>保存中にエラーが発生しました</p>"
