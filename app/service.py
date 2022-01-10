from fastapi import FastAPI, HTTPException

from . import ips, models
from .db import db
from .utils import PrettyJSONResponse


app = FastAPI()


@app.get("/", response_class=PrettyJSONResponse)
async def get_ruc(ruc):
    result = await models.Ruc.retreive(db, ruc)
    if result is None:
        raise HTTPException(status_code=404, detail="Ruc no encontrado")
    return result


@app.get("/ips", response_class=PrettyJSONResponse)
async def get_ruc(documento):
    try:
        return ips.consulta_asegurado(documento)
    except ips.IPSException:
        raise HTTPException(status_code=502, detail="No se pudo obtener una respuesta a tiempo")

