from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException

from . import ips, models
from .db import db, db_1
from .utils import PrettyJSONResponse

app = FastAPI()


@app.get("/", response_class=PrettyJSONResponse)
async def get_ruc(ruc):
    result = await models.Ruc.retreive(db, ruc)
    if result is None:
        raise HTTPException(status_code=404, detail="Ruc no encontrado")
    return result


@app.get("/ips", response_class=PrettyJSONResponse)
async def get_ips(documento):
    try:
        return ips.consulta_asegurado(documento)
    except ips.IPSException:
        raise HTTPException(status_code=502, detail="No se pudo obtener una respuesta a tiempo")


@app.get("/personas", response_class=PrettyJSONResponse)
async def get_persona(cedula):
    result = await models.Persona.retreive(db_1, cedula)
    if result is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    s = str(result.fecnac)
    fecnac = datetime(year=int(s[0:4]), month=int(s[4:6]), day=int(s[6:8]))
    return {
        "cedula": result.id,
        "apellidos": result.apellidos,
        "nombres": result.nombres,
        "fecNac": fecnac.strftime("%d/%m/%Y")
    }
