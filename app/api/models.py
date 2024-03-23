from sqlalchemy import Column, Integer, DateTime, Numeric, String
from api.database import Base

class AptEstymations(Base):
    __tablename__ = 'apt_estymations'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    lat = Column(Numeric(precision=9, scale=6))
    lng = Column(Numeric(precision=9, scale=6))
    market = Column(String(14))
    build_year = Column(Integer)
    area = Column(Integer)
    rooms = Column(Integer)
    floor = Column(Integer)
    floors = Column(Integer)
    ann_price = Column(Integer)
    ann_price_m2 = Column(Integer)
    xgb_price = Column(Integer)
    xgb_price_m2 = Column(Integer)
    source = Column(String(3))
    ip_address = Column(String(39))
