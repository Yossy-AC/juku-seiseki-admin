from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.models.student import Student
from app.models.class_ import Class

router = APIRouter()

@router.get("", response_class=HTMLResponse)
async def list_students(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    """生徒一覧（HTMX用）"""
    students = db.query(Student).all()

    if not students:
        return "<p>生徒が登録されていません</p>"

    rows = "".join([
        f"""<tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">{s.name}</td>
            <td style="padding: 10px;">{s.name_kana or '-'}</td>
            <td style="padding: 10px;">{s.target_university or '-'}</td>
            <td style="padding: 10px;">{s.target_dept or '-'}</td>
            <td style="padding: 10px; text-align: center;">{s.gender or '-'}</td>
        </tr>"""
        for s in students
    ])

    return f"""
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
            <tr style="background: #667eea; color: white;">
                <th style="padding: 10px; text-align: left;">氏名</th>
                <th style="padding: 10px; text-align: left;">ふりがな</th>
                <th style="padding: 10px; text-align: left;">志望大学</th>
                <th style="padding: 10px; text-align: left;">志望学部</th>
                <th style="padding: 10px; text-align: center;">性別</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """

@router.post("", response_class=HTMLResponse)
async def create_student(db: Session = Depends(get_db), _: None = Depends(require_auth)):
    """生徒追加（HTMX用）"""
    return "<p>生徒追加は Phase 3 後期で実装予定</p>"
