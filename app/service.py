import os
from io import BytesIO, StringIO
from typing import List, Optional

import pandas as pd
import sqlalchemy
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from . import _set, ips, mimetypes, models
from .conf import settings
from .db import db, db_1, metadata_1
from .utils import PrettyJSONResponse, download, get_delimitter, str_to_datestr

RUC_DB_PATH = str(db.url).replace("sqlite:///", "")
PERSONA_DB_PATH = str(db_1.url).replace("sqlite:///", "")


def ensure_db():
    if not os.path.exists(RUC_DB_PATH):
        print("Database does not exist")
        print("Checking environment variables for database url")
        if settings.RUC_DB_URL is not None:
            print("RUC_DB_URL found, downloading database")
            download(settings.RUC_DB_URL, RUC_DB_PATH)
        else:
            print("RUC_DB_URL not found, starting crawler")
            crawler = _set.RucCrawler()
            crawler.run()
    else:
        print("RUC database found")

    if not os.path.exists(PERSONA_DB_PATH):
        if settings.PEOPLE_DB_URL is not None:
            print("PEOPLE_DB_URL found, downloading database")
            download(settings.PEOPLE_DB_URL, PERSONA_DB_PATH)
        else:
            print("PEOPLE_DB_URL not found, awaiting for creation")

    else:
        print("People database found")


ensure_db()
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_headers=["*"], allow_methods=["*"]
)


@app.on_event("startup")
async def startup():
    if not os.path.exists(PERSONA_DB_PATH) and settings.PEOPLE_DB_URL is None:
        print("Creating people database")
        await db_1.connect()
        engine = sqlalchemy.create_engine(str(db_1.url))
        print(f"engine: {engine}")
        metadata_1.create_all(engine)
        await db_1.disconnect()


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


@app.get("/search", response_class=PrettyJSONResponse)
async def search(query):
    query = query.strip()
    results = await models.Ruc.search(db, query)
    if len(results) == 0 and query.isdigit():
        results = [await models.Persona.get_ruc(db_1, query)]
        if results[0] is None:
            try:
                results = [_set.get_taxpayer(query)]
            except (Exception, _set.DoesNotExist) as e:
                results = []
    return results


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
        "cedula": result.cedula,
        "apellidos": result.apellidos,
        "nombres": result.nombres,
        "fecNac": str_to_datestr(result.nacimiento),
    }


class Document(BaseModel):
    id: str


@app.post("/names", response_class=PrettyJSONResponse)
async def set_names(documents: List[Document]):
    ids = [d.id for d in documents]
    people = await models.Persona.get_dict(db_1, ids)
    data = {str(k): v.razonsocial for k, v in people.items()}
    ids = list(set(ids) - set(data.keys()))
    tax_payers = await models.Ruc.get_dict(db, ids)
    data.update({str(k): v.razonsocial for k, v in tax_payers.items()})
    return data


@app.post("/validate-ruc", response_class=PrettyJSONResponse)
async def create_upload_file(
    file: Optional[UploadFile] = File(None),
    index: str = Form("0"),
    rg90: bool = Form(False),
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
    counter = {
        "RUC INEXISTENTE": 0,
        "CANCELADO": 0,
        "SUSPENSION TEMPORAL": 0,
        "BLOQUEADO": 0,
    }
    for i, row in df.iterrows():
        document_type = None
        if rg90:
            document_type = str(row[1])
        raw = " ".join([str(x) for x in row])
        ruc = str(row[int(index) - 1])
        if ruc != "X" and (document_type == "11" or document_type is None):
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
                counter["RUC INEXISTENTE"] += 1
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
                    counter[instance.estado] += 1
    return {"invalid_list": invalid_list, "counter": counter}
