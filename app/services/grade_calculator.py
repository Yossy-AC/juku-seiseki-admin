"""
成績計算ロジック
既存の dataLoader.js の calculateClassAverage, calculateStudentAverage, calculateAttendanceRate をPython化
"""

from typing import List
from datetime import date
from sqlalchemy.orm import Session
from app.models.grade import Grade
from app.models.student import Student
from app.models.attendance import Attendance

def get_student_grades(db: Session, student_id: str) -> List[Grade]:
    """特定の生徒の成績を取得（日付でソート）"""
    return db.query(Grade)\
        .filter(Grade.student_id == student_id)\
        .order_by(Grade.date)\
        .all()

def get_student_attendance(db: Session, student_id: str) -> List[Attendance]:
    """特定の生徒の出席記録を取得（日付でソート）"""
    return db.query(Attendance)\
        .filter(Attendance.student_id == student_id)\
        .order_by(Attendance.date)\
        .all()

def get_class_grades(db: Session, class_id: str) -> List[Grade]:
    """特定の講座に属する全生徒の成績を取得"""
    return db.query(Grade)\
        .join(Student, Grade.student_id == Student.id)\
        .filter(Student.class_id == class_id)\
        .all()

def calculate_student_average(db: Session, student_id: str) -> int:
    """
    特定の生徒の平均スコア（0-100）を計算
    各成績の score_total を 0-100 にスケールして平均を計算
    """
    grades = get_student_grades(db, student_id)

    if not grades:
        return 0

    total_score = 0
    for grade in grades:
        # スコアを 0-100 にスケール
        normalized_score = (grade.score_total / grade.max_total * 100) if grade.max_total else 0
        total_score += normalized_score

    return round(total_score / len(grades))

def calculate_class_average(db: Session, class_id: str, target_date: date = None) -> int:
    """
    特定の講座（クラス）の平均スコア（0-100）を計算

    Args:
        db: DB セッション
        class_id: 講座ID
        target_date: 特定の日付のみ計算する場合

    Returns:
        0-100 のスコア
    """
    grades = get_class_grades(db, class_id)

    # 特定の日付の成績に絞る場合
    if target_date:
        grades = [g for g in grades if g.date == target_date]

    if not grades:
        return 0

    total_score = 0
    for grade in grades:
        # スコアを 0-100 にスケール
        normalized_score = (grade.score_total / grade.max_total * 100) if grade.max_total else 0
        total_score += normalized_score

    return round(total_score / len(grades))

def calculate_attendance_rate(db: Session, student_id: str) -> int:
    """
    特定の生徒の出席率（0-100）を計算

    Returns:
        出席率（パーセント）
    """
    records = get_student_attendance(db, student_id)

    if not records:
        return 0

    present_count = sum(1 for r in records if r.status == "出席")
    return round((present_count / len(records)) * 100)

def get_attendance_summary(db: Session, student_id: str) -> dict:
    """
    出席状況のサマリーを取得

    Returns:
        {"present": 出席数, "absent": 欠席数, "late": 遅刻数, "rate": 出席率}
    """
    records = get_student_attendance(db, student_id)

    if not records:
        return {"present": 0, "absent": 0, "late": 0, "rate": 0}

    present = sum(1 for r in records if r.status == "出席")
    absent = sum(1 for r in records if r.status == "欠席")
    late = sum(1 for r in records if r.status == "遅刻")
    rate = round((present / len(records)) * 100)

    return {
        "present": present,
        "absent": absent,
        "late": late,
        "rate": rate,
        "total": len(records)
    }

def get_grade_summary(db: Session, student_id: str) -> dict:
    """
    生徒の成績サマリーを取得

    Returns:
        {
            "grades": [成績レコードのリスト],
            "average": 平均スコア,
            "count": 成績数,
            "latest": 最新の成績スコア
        }
    """
    grades = get_student_grades(db, student_id)

    if not grades:
        return {
            "grades": [],
            "average": 0,
            "count": 0,
            "latest": None
        }

    average = calculate_student_average(db, student_id)
    latest = grades[-1].score_total if grades else None

    return {
        "grades": grades,
        "average": average,
        "count": len(grades),
        "latest": latest
    }

def generate_advice(db: Session, student_id: str) -> str:
    """
    学習アドバイスを生成（簡易版）

    実装のプレースホルダー
    将来的には AI を使った分析に置き換え可能
    """
    summary = get_grade_summary(db, student_id)
    attendance = get_attendance_summary(db, student_id)

    if summary["count"] == 0:
        return "成績データがまだ登録されていません。"

    average = summary["average"]
    attendance_rate = attendance["rate"]

    advice_list = []

    # 成績に基づくアドバイス
    if average >= 80:
        advice_list.append("成績が優秀です。このペースを保ってください。")
    elif average >= 60:
        advice_list.append("成績は安定しています。さらなる向上を目指しましょう。")
    else:
        advice_list.append("成績の向上が必要です。苦手な分野に集中して取り組んでください。")

    # 出席に基づくアドバイス
    if attendance_rate == 100:
        advice_list.append("出席率100％です。その調子で頑張ってください！")
    elif attendance_rate >= 90:
        advice_list.append("出席率が良好です。欠席をしないようにしましょう。")
    elif attendance_rate >= 80:
        advice_list.append("出席率を改善してください。")
    else:
        advice_list.append("出席率が低下しています。授業への参加を重視してください。")

    return " ".join(advice_list)
