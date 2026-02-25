from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.models.student import Student
from app.services.grade_calculator import get_attendance_summary

router = APIRouter()

@router.get("/student/{student_id}", response_class=HTMLResponse)
async def get_attendance(student_id: str, db: Session = Depends(get_db), _: None = Depends(require_auth)):
    """出席状況（HTMX用）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return "<p>生徒が見つかりません</p>"

    summary = get_attendance_summary(db, student_id)

    if summary["total"] == 0:
        return "<p>出席記録がありません</p>"

    # 出席バー表示
    present_percent = round((summary["present"] / summary["total"]) * 100) if summary["total"] else 0

    return f"""
    <div style="background: #f9f9f9; padding: 1.5rem; border-radius: 8px;">
        <h3 style="margin-top: 0; margin-bottom: 1rem; color: #333;">出席率: {summary['rate']}% ({summary['present']}/{summary['total']})</h3>

        <div style="background: white; border-radius: 4px; overflow: hidden; margin-bottom: 1.5rem;">
            <div style="height: 30px; background: linear-gradient(to right, #4CAF50 0%, #4CAF50 {present_percent}%, #e0e0e0 {present_percent}%, #e0e0e0 100%); border-radius: 4px; position: relative;">
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div style="background: #e8f5e9; padding: 1rem; border-radius: 8px; text-align: center;">
                <p style="margin: 0; font-size: 0.9rem; color: #2e7d32;">出席</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: #2e7d32;">{summary['present']}</p>
            </div>
            <div style="background: #ffebee; padding: 1rem; border-radius: 8px; text-align: center;">
                <p style="margin: 0; font-size: 0.9rem; color: #c62828;">欠席</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: #c62828;">{summary['absent']}</p>
            </div>
            <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; text-align: center;">
                <p style="margin: 0; font-size: 0.9rem; color: #e65100;">遅刻</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: #e65100;">{summary['late']}</p>
            </div>
        </div>
    </div>
    """

@router.post("", response_class=HTMLResponse)
async def create_attendance(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    """出席記録追加（HTMX用）"""
    return "<p>出席記録追加は Phase 3 で実装予定</p>"
