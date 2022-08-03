import csv
from io import BytesIO, StringIO
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

from . import _set, ips, mimetypes, models
from .db import db, db_1
from .utils import PrettyJSONResponse, get_delimitter, int_to_datestr

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"]
)


@app.get("/", response_class=PrettyJSONResponse)
async def get_ruc(ruc):
    data = await models.Ruc.retreive(db, ruc)
    if data is None:
        data = await models.Persona.get_ruc(db_1, ruc)
        if data is None:
            try:
                data = _set.get_taxpayer(ruc)
            except (Exception, _set.DoesNotExist) as e:
                raise HTTPException(status_code=404, detail="No encontrado")
    elif data.tipo == "F":
        _data = await models.Persona.get_ruc(db_1, ruc)
        if _data is not None:
            _data["dv"] = data.dv
            _data["estado"] = data.estado
            data = _data
    return data


@app.get("/ips", response_class=PrettyJSONResponse)
async def get_ips(documento):
    try:
        return ips.consulta_asegurado(documento)
    except ips.IPSException:
        raise HTTPException(
            status_code=502, detail="No se pudo obtener una respuesta a tiempo"
        )


@app.get("/personas", response_class=PrettyJSONResponse)
async def get_persona(cedula):
    result = await models.Persona.retreive(db_1, cedula)
    if result is None:
        ruc = await models.Ruc.retreive(db, cedula)
        if ruc is None or ruc.tipo != "F":
            try:
                return _set.get_citizen(cedula)
            except (Exception, _set.DoesNotExist) as e:
                raise HTTPException(status_code=404, detail="Persona no encontrada")
        return {
            "cedula": ruc.ruc,
            "apellidos": "",
            "nombres": ruc.razonsocial,
            "fecNac": None,
        }
    return {
        "cedula": result.id,
        "apellidos": result.apellidos,
        "nombres": result.nombres,
        "fecNac": int_to_datestr(result.fecnac),
    }


@app.post("/validate-ruc", response_class=PrettyJSONResponse)
async def create_upload_file(
    file: Optional[UploadFile] = File(None), index: str = Form("0")
):
    if file.content_type not in [
        mimetypes.TEXT_PLAIN,
        mimetypes.CSV,
        mimetypes.MS_EXCEL,
        mimetypes.SHEET,
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"File type of {file.content_type} is not supported",
        )

    df = None
    offset = 0

    if file.content_type == mimetypes.SHEET:
        offset = 1
        contents = await file.read()
        data = BytesIO(contents)
        df = pd.read_excel(data, header=None)

    if file.content_type in (mimetypes.TEXT_PLAIN, mimetypes.CSV):
        offset = 2
        buffer = StringIO(str(file.file.read(), "utf-8"))
        delimiter = get_delimitter(buffer)
        df = pd.read_csv(buffer, header=None, encoding="utf-8", sep=delimiter)

    if df is None:
        raise HTTPException(status_code=400, detail="Missing dataframe")

    rucs = [str(row[int(index) - 1]) for i, row in df.iterrows()]
    data = await models.Ruc.get_dict(db, rucs)

    invalid_list = []
    for i, row in df.iterrows():
        raw = " ".join([str(x) for x in row])
        ruc = str(row[int(index) - 1])
        instance = data.get(ruc)
        if instance is None:
            invalid_list.append(
                {
                    "row": i + offset,
                    "data": raw,
                    "ruc": ruc,
                    "msg": "RUC INEXISTENTE",
                }
            )
        else:
            if instance.estado != "ACTIVO":
                invalid_list.append(
                    {
                        "row": i + offset,
                        "data": raw,
                        "ruc": ruc,
                        "msg": instance.estado,
                    }
                )
    return {"invalid_list": invalid_list}
