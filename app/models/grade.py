from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Grade(Base):
    __tablename__ = "grades"

    id = Column(String(30), primary_key=True)       # "g001"
    student_id = Column(String(20), ForeignKey("students.id"), nullable=False)
    class_id = Column(String(20), ForeignKey("classes.id"))
    date = Column(Date, nullable=False)
    lesson_number = Column(Integer)
    lesson_content = Column(String(200))

    # scores（各科目の得点を個別カラムに）
    score_comprehension = Column(Integer, default=0)
    score_unseen = Column(Integer, default=0)
    score_grammar = Column(Integer, default=0)
    score_vocabulary = Column(Integer, default=0)
    score_listening = Column(Integer, default=0)
    score_total = Column(Integer, default=0)

    # maxScores（現在は全生徒共通だが将来の柔軟性のため保持）
    max_comprehension = Column(Integer, default=20)
    max_unseen = Column(Integer, default=20)
    max_grammar = Column(Integer, default=20)
    max_vocabulary = Column(Integer, default=20)
    max_listening = Column(Integer, default=20)
    max_total = Column(Integer, default=100)

    student = relationship("Student", back_populates="grades")
    class_ = relationship("Class")
