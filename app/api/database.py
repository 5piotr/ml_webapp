import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

user = 'piotr'
password = os.environ['MYSQL_PASSWORD']
host = 'mysql_apt_db'
database = 'apt_db'

SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{user}:{password}@{host}/{database}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
