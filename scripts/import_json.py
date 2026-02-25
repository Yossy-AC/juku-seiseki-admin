#!/usr/bin/env python3
"""
既存 JSON ファイルから SQLite へのデータ移行スクリプト

実行: uv run python scripts/import_json.py
"""

import json
from pathlib import Path
from datetime import date
import sys

# プロジェクトルートを sys.path に追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, create_db_and_tables
from app.models.class_ import Class
from app.models.student import Student
from app.models.grade import Grade
from app.models.attendance import Attendance

DATA_DIR = Path(__file__).parent.parent / "data"

def import_classes(session):
    """講座データをインポート"""
    print("📚 講座データをインポート中...")
    data_file = DATA_DIR / "classes.json"

    if not data_file.exists():
        print(f"  ⚠️  {data_file} が見つかりません")
        return

    data = json.loads(data_file.read_text(encoding="utf-8"))
    for c in data.get("classes", []):
        existing = session.query(Class).filter(Class.id == c["id"]).first()
        if not existing:
            session.add(Class(
                id=c["id"],
                name=c["name"],
                day=c.get("day"),
                time=c.get("time"),
                capacity=c.get("capacity", 30)
            ))
            print(f"  ✓ {c['name']}")

    session.commit()
    print(f"  完了: {len(data.get('classes', []))} 件の講座")

def import_students(session):
    """生徒データをインポート"""
    print("👥 生徒データをインポート中...")
    data_file = DATA_DIR / "students.json"

    if not data_file.exists():
        print(f"  ⚠️  {data_file} が見つかりません")
        return

    data = json.loads(data_file.read_text(encoding="utf-8"))
    for s in data.get("students", []):
        existing = session.query(Student).filter(Student.id == s["id"]).first()
        if not existing:
            join_date = None
            if s.get("joinDate"):
                try:
                    join_date = date.fromisoformat(s["joinDate"])
                except ValueError:
                    pass

            session.add(Student(
                id=s["id"],
                name=s["name"],
                name_kana=s.get("nameKana"),
                classroom=s.get("classroom"),
                gender=s.get("gender"),
                high_school=s.get("highSchool"),
                course_subject=s.get("courseSubject"),
                school_class=s.get("schoolClass"),
                club=s.get("club"),
                target_university=s.get("targetUniversity"),
                target_dept=s.get("targetDept"),
                class_id=s.get("classId"),
                join_date=join_date
            ))
            print(f"  ✓ {s['name']}")

    session.commit()
    print(f"  完了: {len(data.get('students', []))} 件の生徒")

def import_grades(session):
    """成績データをインポート"""
    print("📊 成績データをインポート中...")
    data_file = DATA_DIR / "grades.json"

    if not data_file.exists():
        print(f"  ⚠️  {data_file} が見つかりません")
        return

    data = json.loads(data_file.read_text(encoding="utf-8"))
    count = 0
    for g in data.get("grades", []):
        existing = session.query(Grade).filter(Grade.id == g["id"]).first()
        if not existing:
            scores = g.get("scores", {})
            max_scores = g.get("maxScores", {})

            grade_date = None
            if g.get("date"):
                try:
                    grade_date = date.fromisoformat(g["date"])
                except ValueError:
                    pass

            session.add(Grade(
                id=g["id"],
                student_id=g["studentId"],
                class_id=g.get("classId"),
                date=grade_date,
                lesson_number=g.get("lessonNumber"),
                lesson_content=g.get("lessonContent"),
                score_comprehension=scores.get("comprehension", 0),
                score_unseen=scores.get("unseenProblems", 0),
                score_grammar=scores.get("grammar", 0),
                score_vocabulary=scores.get("vocabulary", 0),
                score_listening=scores.get("listening", 0),
                score_total=scores.get("total", 0),
                max_comprehension=max_scores.get("comprehension", 20),
                max_unseen=max_scores.get("unseenProblems", 20),
                max_grammar=max_scores.get("grammar", 20),
                max_vocabulary=max_scores.get("vocabulary", 20),
                max_listening=max_scores.get("listening", 20),
                max_total=max_scores.get("total", 100),
            ))
            count += 1
            print(f"  ✓ 成績ID: {g['id']}")

    session.commit()
    print(f"  完了: {count} 件の成績")

def import_attendance(session):
    """出席データをインポート"""
    print("📋 出席データをインポート中...")
    data_file = DATA_DIR / "attendance.json"

    if not data_file.exists():
        print(f"  ⚠️  {data_file} が見つかりません")
        return

    data = json.loads(data_file.read_text(encoding="utf-8"))
    count = 0
    for a in data.get("attendance", []):
        existing = session.query(Attendance).filter(Attendance.id == a["id"]).first()
        if not existing:
            att_date = None
            if a.get("date"):
                try:
                    att_date = date.fromisoformat(a["date"])
                except ValueError:
                    pass

            session.add(Attendance(
                id=a["id"],
                student_id=a["studentId"],
                class_id=a.get("classId"),
                date=att_date,
                status=a["status"]
            ))
            count += 1
            print(f"  ✓ 出席ID: {a['id']}")

    session.commit()
    print(f"  完了: {count} 件の出席記録")

def main():
    print("=" * 60)
    print("JSON → SQLite データ移行スクリプト")
    print("=" * 60)
    print()

    # DB テーブル作成
    print("🔧 データベーステーブルを作成中...")
    create_db_and_tables()
    print("  ✓ テーブル作成完了\n")

    # データインポート
    session = SessionLocal()
    try:
        import_classes(session)
        print()
        import_students(session)
        print()
        import_grades(session)
        print()
        import_attendance(session)
        print()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()

    print("=" * 60)
    print("✅ データ移行が完了しました")
    print("=" * 60)

if __name__ == "__main__":
    main()
