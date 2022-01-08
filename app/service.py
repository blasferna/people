from fastapi import FastAPI

from .db import db
from . import models

app = FastAPI()

@app.get("/")
async def get(ruc):
    return await models.Ruc.retreive(db, ruc)
