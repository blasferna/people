import sqlalchemy

from .db import metadata, metadata_1
from .utils import int_to_datestr


rucs = sqlalchemy.Table(
    "ruc",
    metadata,
    sqlalchemy.Column("ruc", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("razonsocial", sqlalchemy.String),
    sqlalchemy.Column("tipo", sqlalchemy.String),
    sqlalchemy.Column("categoria", sqlalchemy.String),
    sqlalchemy.Column("dv", sqlalchemy.String),
    sqlalchemy.Column("estado", sqlalchemy.String)
)

personas = sqlalchemy.Table(
    "cedulas",
    metadata_1,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("apellidos", sqlalchemy.String),
    sqlalchemy.Column("nombres", sqlalchemy.String),
    sqlalchemy.Column("fecnac", sqlalchemy.Integer)
)

class Ruc:
    @staticmethod
    async def retreive(db, ruc):
        return await db.fetch_one(rucs.select().where(rucs.c.ruc==ruc))

class Persona:
    @staticmethod
    async def retreive(db, cedula):
        return await db.fetch_one(personas.select().where(personas.c.id==cedula))
    
    @staticmethod
    async def get_ruc(db, cedula):
        data = await Persona.retreive(db, cedula)
        if data is not None:
            return {
                "ruc": data.id,
                "razonsocial": f"{data.apellidos} {data.nombres}",
                "tipo": "F",
                "categoria": 0,
                "dv": None,
                "fecNac": int_to_datestr(data.fecnac),
                "estado": ""
            }
        return None
