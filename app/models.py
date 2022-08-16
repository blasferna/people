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
    sqlalchemy.Column("estado", sqlalchemy.String),
)

personas = sqlalchemy.Table(
    "cedulas",
    metadata_1,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("apellidos", sqlalchemy.String),
    sqlalchemy.Column("nombres", sqlalchemy.String),
    sqlalchemy.Column("fecnac", sqlalchemy.Integer),
)


class Ruc:
    @staticmethod
    async def retreive(db, ruc):
        return await db.fetch_one(rucs.select().where(rucs.c.ruc == ruc))

    @staticmethod
    async def filter_by_rucs(db, _rucs):
        _in = ",".join(map(lambda x: f"'{x}'", _rucs))
        sql = f"SELECT r.ruc, r.razonsocial, r.categoria, r.estado FROM ruc r WHERE r.ruc IN ({_in})"
        return await db.fetch_all(sql)

    @staticmethod
    async def get_dict(db, _rucs):
        data = await Ruc.filter_by_rucs(db, _rucs)
        return {x.ruc: x for x in data}


class Persona:
    @staticmethod
    async def retreive(db, cedula):
        return await db.fetch_one(personas.select().where(personas.c.id == cedula))

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
                "estado": "",
            }
        return None
