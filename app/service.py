from fastapi import FastAPI, HTTPException

from . import ips, models
from .db import db, db_1
from .utils import PrettyJSONResponse, int_to_datestr

app = FastAPI()


@app.get("/", response_class=PrettyJSONResponse)
async def get_ruc(ruc):
    data = await models.Ruc.retreive(db, ruc)
    if data is None:
        data = await models.Persona.get_ruc(db_1, ruc)
        if data is None:
            raise HTTPException(status_code=404, detail="No encontrado")
    elif data.tipo == "F":
        _data = await models.Persona.get_ruc(db_1, ruc)
        if _data is not None:
            _data['dv'] = data.dv
            data = _data
    return data


@app.get("/ips", response_class=PrettyJSONResponse)
async def get_ips(documento):
    try:
        return ips.consulta_asegurado(documento)
    except ips.IPSException:
        raise HTTPException(
            status_code=502, detail="No se pudo obtener una respuesta a tiempo")


@app.get("/personas", response_class=PrettyJSONResponse)
async def get_persona(cedula):
    result = await models.Persona.retreive(db_1, cedula)
    if result is None:
        ruc = await models.Ruc.retreive(db, cedula)
        if ruc is None or ruc.tipo != 'F':
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        return {
            "cedula": ruc.ruc,
            "apellidos": "",
            "nombres": ruc.razonsocial,
            "fecNac": None
        }
    return {
        "cedula": result.id,
        "apellidos": result.apellidos,
        "nombres": result.nombres,
        "fecNac": int_to_datestr(result.fecnac)
    }
