from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.class_ import Class
from app.models.student import Student

router = APIRouter()

@router.get("", response_class=HTMLResponse)
async def list_classes(db: Session = Depends(get_db)):
    """講座一覧（HTMX用）"""
    classes = db.query(Class).all()

    if not classes:
        return "<p>講座が登録されていません</p>"

    rows = "".join([
        f"""<tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">{c.name}</td>
            <td style="padding: 10px;">{c.day or '-'}</td>
            <td style="padding: 10px;">{c.time or '-'}</td>
            <td style="padding: 10px; text-align: center;">{len(c.students) if c.students else 0}</td>
        </tr>"""
        for c in classes
    ])

    return f"""
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
            <tr style="background: #667eea; color: white;">
                <th style="padding: 10px; text-align: left;">講座名</th>
                <th style="padding: 10px; text-align: left;">曜日</th>
                <th style="padding: 10px; text-align: left;">時間</th>
                <th style="padding: 10px; text-align: center;">生徒数</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """

@router.get("/{class_id}/students", response_class=HTMLResponse)
async def get_class_students(class_id: str, db: Session = Depends(get_db)):
    """講座別生徒セレクトボックス（HTMX用、連鎖セレクト）"""
    students = db.query(Student).filter(Student.class_id == class_id).all()

    if not students:
        return """
        <select name="student_id" required disabled>
            <option value="">この講座に生徒がいません</option>
        </select>
        """

    options = "".join([
        f'<option value="{s.id}">{s.name}</option>'
        for s in students
    ])

    return f"""
    <select name="student_id" required>
        <option value="">生徒を選択</option>
        {options}
    </select>
    """
