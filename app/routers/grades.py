from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.services.grade_calculator import (
    get_student_grades,
    calculate_student_average,
    calculate_class_average,
    generate_advice
)

router = APIRouter()

@router.get("/student/{student_id}", response_class=HTMLResponse)
async def get_student_grades_html(student_id: str, db: Session = Depends(get_db)):
    """生徒別成績テーブル（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"

    grades = get_student_grades(db, student_id)

    if not grades:
        return "<p>成績データがありません</p>"

    # HTML テーブル生成
    rows = "".join([
        f"""<tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">{grade.date}</td>
            <td style="padding: 10px;">{grade.lesson_content or '-'}</td>
            <td style="padding: 10px; text-align: center;">{grade.score_comprehension}/{grade.max_comprehension}</td>
            <td style="padding: 10px; text-align: center;">{grade.score_unseen}/{grade.max_unseen}</td>
            <td style="padding: 10px; text-align: center;">{grade.score_grammar}/{grade.max_grammar}</td>
            <td style="padding: 10px; text-align: center;">{grade.score_vocabulary}/{grade.max_vocabulary}</td>
            <td style="padding: 10px; text-align: center;">{grade.score_listening}/{grade.max_listening}</td>
            <td style="padding: 10px; text-align: center; font-weight: bold;">{grade.score_total}/{grade.max_total}</td>
        </tr>"""
        for grade in grades
    ])

    return f"""
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
            <tr style="background: #667eea; color: white;">
                <th style="padding: 10px; text-align: left;">日付</th>
                <th style="padding: 10px; text-align: left;">授業内容</th>
                <th style="padding: 10px; text-align: center;">理解</th>
                <th style="padding: 10px; text-align: center;">初見</th>
                <th style="padding: 10px; text-align: center;">文法</th>
                <th style="padding: 10px; text-align: center;">単語</th>
                <th style="padding: 10px; text-align: center;">リスニング</th>
                <th style="padding: 10px; text-align: center;">合計</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """

@router.get("/comparison/{student_id}", response_class=HTMLResponse)
async def get_comparison(student_id: str, db: Session = Depends(get_db)):
    """クラス平均比較（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"

    student_avg = calculate_student_average(db, student_id)
    class_avg = calculate_class_average(db, student.class_id) if student.class_id else 0
    difference = student_avg - class_avg

    difference_color = "#2e7d32" if difference >= 0 else "#c62828"
    difference_sign = "+" if difference >= 0 else ""

    return f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
        <div style="background: #f0f0f0; padding: 1rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0; font-size: 0.9rem; color: #666;">あなたの平均</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold; color: #667eea;">{student_avg}点</p>
        </div>
        <div style="background: #f0f0f0; padding: 1rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0; font-size: 0.9rem; color: #666;">クラス平均</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold; color: #666;">{class_avg}点</p>
        </div>
        <div style="background: #f0f0f0; padding: 1rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0; font-size: 0.9rem; color: #666;">差（クラス比）</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold; color: {difference_color};">{difference_sign}{difference}点</p>
        </div>
    </div>
    """

@router.get("/advice/{student_id}", response_class=HTMLResponse)
async def get_advice(student_id: str, db: Session = Depends(get_db)):
    """学習アドバイス（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"

    advice = generate_advice(db, student_id)

    return f"""
    <div style="border-left: 4px solid #667eea; background: #f8f9fa; padding: 1rem; border-radius: 8px;">
        <p style="line-height: 1.8; color: #555; margin: 0;">{advice}</p>
    </div>
    """

@router.post("", response_class=HTMLResponse)
async def create_grade(db: Session = Depends(get_db)):
    """成績入力（HTMX用）"""
    return "<p>成績入力は Phase 3 で実装予定</p>"
