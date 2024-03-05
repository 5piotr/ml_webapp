from fastapi import FastAPI
from . import models
from .database import engine
from .routers import rps, apt_estimator

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(rps.router)
app.include_router(apt_estimator.router)
