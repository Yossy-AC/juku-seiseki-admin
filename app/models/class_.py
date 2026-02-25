from sqlalchemy import Column, String, Integer
from app.database import Base

class Class(Base):
    __tablename__ = "classes"

    id = Column(String(20), primary_key=True)  # "class001"
    name = Column(String(100), nullable=False)  # "高3英語@難関大"
    day = Column(String(10))                    # "月"
    time = Column(String(20))                   # "19:00-20:30"
    capacity = Column(Integer, default=30)
