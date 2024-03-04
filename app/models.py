from .database import Base
from sqlalchemy import Column, Integer, DateTime, Float, String

class UserEstymations(Base):
    __tablename__ = 'user_requests'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    lat = Column(Float)
    lng = Column(Float)
    market = Column(String(14))
    build_year = Column(Integer)
    area = Column(Float)
    rooms = Column(Integer)
    floor = Column(Integer)
    floors = Column(Integer)
    ann_price = Column(Float)
    xgb_price = Column(Float)
