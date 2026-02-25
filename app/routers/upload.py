import logging
import uuid
from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.services.csv_importer import (
    parse_new_format_csv,
    match_students_to_ids,
    match_grades_to_students,
    save_csv_data,
)
from app.templates_config import templates

logger = logging.getLogger(__name__)
router = APIRouter()

# UUIDキーでキャッシュ。セッションにキーを保存して他ユーザーの改ざんを防ぐ
preview_cache: dict = {}


@router.post("/csv", response_class=HTMLResponse)
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """CSV解析＆プレビュー（HTMX用）"""
    try:
        content = await file.read()
        csv_text = content.decode("utf-8-sig")

        students_raw, grades_raw = parse_new_format_csv(csv_text)
        students_with_ids = match_students_to_ids(db, students_raw)
        matched_grades = match_grades_to_students(db, students_with_ids, grades_raw)

        # セッションにUUIDキーを保存（外部改ざん防止）
        cache_key = str(uuid.uuid4())
        preview_cache[cache_key] = {
            "students_with_ids": students_with_ids,
            "matched_grades": matched_grades,
        }
        request.session["upload_cache_key"] = cache_key

        return templates.TemplateResponse(
            "partials/upload_preview.html",
            {
                "request": request,
                "students": students_with_ids,
                "grades": matched_grades,
            },
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "partials/upload_error.html",
            {"request": request, "message": str(e)},
        )
    except Exception as e:
        logger.error("CSV upload error: %s", e, exc_info=True)
        return templates.TemplateResponse(
            "partials/upload_error.html",
            {"request": request, "message": "ファイルの処理中にエラーが発生しました"},
        )


@router.post("/save", response_class=HTMLResponse)
async def save_csv(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_auth),
):
    """保存確定（HTMX用）"""
    try:
        # セッションからキーを取得（外部からの偽装を防ぐ）
        cache_key = request.session.pop("upload_cache_key", None)
        if not cache_key or cache_key not in preview_cache:
            raise ValueError("プレビューデータが見つかりません。もう一度アップロードしてください。")

        data = preview_cache.pop(cache_key)
        results = save_csv_data(db, data["students_with_ids"], data["matched_grades"])

        return templates.TemplateResponse(
            "partials/upload_success.html",
            {
                "request": request,
                "added_students": results["added_students"],
                "updated_students": results["updated_students"],
                "added_grades": results["added_grades"],
                "errors": results["errors"],
            },
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "partials/upload_error.html",
            {"request": request, "message": str(e)},
        )
    except Exception as e:
        logger.error("CSV save error: %s", e, exc_info=True)
        return templates.TemplateResponse(
            "partials/upload_error.html",
            {"request": request, "message": "保存中にエラーが発生しました"},
        )


@router.get("/template")
async def download_template(_: None = Depends(require_auth)):
    """CSVテンプレートダウンロード"""
    template = (
        "【生徒データ】セクション\r\n"
        "教室コード,教室,氏名,ｼﾒｲ,性,高校,学科,学校ｸﾗｽ,部活,志望大学,志望学部\r\n"
        "c001,難関大クラス,学生太郎,がくせいたろう,男,東京高校,理系,3-A,テニス部,東京大学,工学部\r\n"
        "c001,難関大クラス,学生花子,がくせいはなこ,女,西高校,文系,2-B,茶道部,京都大学,法学部\r\n"
        "\r\n"
        "【チェックテスト成績】セクション\r\n"
        "氏名,授業回,授業内容,日付,授業内容の理解,初見問題,文法語法,単語,リスニング,合計\r\n"
        "学生太郎,1,Unit 1 Grammar,2025-01-15,18,15,16,18,17,84\r\n"
        "学生太郎,2,Unit 2 Reading,2025-01-22,19,18,17,19,18,91\r\n"
        "学生花子,1,Unit 1 Grammar,2025-01-15,16,14,15,17,16,78\r\n"
    )
    return Response(
        content=template.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=student_grades_template.csv"
        },
    )
