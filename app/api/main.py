from fastapi import FastAPI
from api.models import Base
from api.database import engine
from api.routers import rps, apt_estimator

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get('/healthy')
def health_check():
    return {'status': 'healthy'}

app.include_router(rps.router)
app.include_router(apt_estimator.router)