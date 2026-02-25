from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
import io
import base64

from app.database import get_db
from app.dependencies import require_auth
from app.services.csv_importer import (
    parse_new_format_csv,
    match_students_to_ids,
    match_grades_to_students,
    generate_preview_html,
    save_csv_data
)

router = APIRouter()

# セッションでプレビューデータを一時保存（実装簡略化のため）
preview_cache = {}

@router.post("/csv", response_class=HTMLResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db), _: None = Depends(require_auth)):
    """CSV解析＆プレビュー（HTMX用）"""
    try:
        # ファイル読み込み
        content = await file.read()
        csv_text = content.decode('utf-8-sig')

        # CSV 解析
        students, grades = parse_new_format_csv(csv_text)

        # 生徒を DB の ID にマッチング
        students_with_ids = match_students_to_ids(db, students)

        # 成績を生徒ID にマッチング
        matched_grades = match_grades_to_students(db, students_with_ids, grades)

        # キャッシュに保存（本来はセッション管理が必要）
        cache_key = base64.b64encode(
            f"{len(students_with_ids)}_{len(matched_grades)}".encode()
        ).decode()
        preview_cache[cache_key] = {
            'students_with_ids': students_with_ids,
            'matched_grades': matched_grades
        }

        # プレビューHTML を生成
        preview_html = generate_preview_html(students_with_ids, matched_grades)

        return f"""
        <div style="background: white; padding: 1.5rem; border-radius: 8px;">
            <h3>プレビュー</h3>
            <p>生徒: {len(students_with_ids)} 件 | 成績: {len(matched_grades)} 件</p>

            {preview_html}

            <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
                <form hx-post="/api/upload/save"
                      hx-target="#preview-area"
                      hx-swap="innerHTML"
                      style="display: inline;">
                    <input type="hidden" name="cache_key" value="{cache_key}">
                    <button type="submit" class="btn btn-primary">保存する</button>
                </form>
                <button type="button" class="btn btn-secondary" onclick="location.reload();">キャンセル</button>
            </div>
        </div>
        """

    except Exception as e:
        return f"""
        <div style="background: #ffebee; color: #c62828; padding: 1rem; border-radius: 8px;">
            <p><strong>エラー:</strong> {str(e)}</p>
        </div>
        """

@router.post("/save", response_class=HTMLResponse)
async def save_csv(cache_key: str, db: Session = Depends(get_db), _: None = Depends(require_auth)):
    """保存確定（HTMX用）"""
    try:
        # キャッシュからデータを取得
        if cache_key not in preview_cache:
            raise ValueError("プレビューデータが見つかりません。もう一度アップロードしてください。")

        data = preview_cache[cache_key]
        students_with_ids = data['students_with_ids']
        matched_grades = data['matched_grades']

        # DB に保存
        results = save_csv_data(db, students_with_ids, matched_grades)

        # キャッシュをクリア
        del preview_cache[cache_key]

        # 成功メッセージ
        error_msg = ""
        if results["errors"]:
            error_msg = f"""
            <div style="background: #fff3e0; color: #e65100; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <strong>警告:</strong>
                <ul style="margin: 0.5rem 0 0 0;">
            """ + "".join([f"<li>{err}</li>" for err in results["errors"]]) + """
                </ul>
            </div>
            """

        return f"""
        <div style="background: #e8f5e9; color: #2e7d32; padding: 1.5rem; border-radius: 8px;">
            {error_msg}
            <h3>保存完了</h3>
            <ul style="margin: 0.5rem 0;">
                <li>追加生徒: {results['added_students']} 件</li>
                <li>更新生徒: {results['updated_students']} 件</li>
                <li>追加成績: {results['added_grades']} 件</li>
            </ul>
            <p style="margin-top: 1rem; color: #666;">ページを再読込すると反映されます。</p>
        </div>
        """

    except Exception as e:
        return f"""
        <div style="background: #ffebee; color: #c62828; padding: 1rem; border-radius: 8px;">
            <p><strong>エラー:</strong> {str(e)}</p>
        </div>
        """

@router.get("/template")
async def download_template(_: None = Depends(require_auth)):
    """CSVテンプレートダウンロード"""
    template = """【生徒データ】セクション
教室コード,教室,氏名,ｼﾒｲ,性,高校,学科,学校ｸﾗｽ,部活,志望大学,志望学部
c001,難関大クラス,学生太郎,がくせいたろう,男,東京高校,理系,3-A,テニス部,東京大学,工学部
c001,難関大クラス,学生花子,がくせいはなこ,女,西高校,文系,2-B,茶道部,京都大学,法学部

【チェックテスト成績】セクション
氏名,授業回,授業内容,日付,授業内容の理解,初見問題,文法語法,単語,リスニング,合計
学生太郎,1,Unit 1 Grammar,2025-01-15,18,15,16,18,17,84
学生太郎,2,Unit 2 Reading,2025-01-22,19,18,17,19,18,91
学生花子,1,Unit 1 Grammar,2025-01-15,16,14,15,17,16,78
"""

    return FileResponse(
        io.BytesIO(template.encode()),
        media_type="text/csv",
        filename="student_grades_template.csv"
    )
