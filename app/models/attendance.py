from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String(20), primary_key=True)
    student_id = Column(String(20), ForeignKey("students.id"), nullable=False)
    class_id = Column(String(20), ForeignKey("classes.id"))
    date = Column(Date, nullable=False)
    status = Column(String(10), nullable=False)   # "出席" / "欠席" / "遅刻"

    student = relationship("Student", back_populates="attendance")
