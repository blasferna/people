import sqlalchemy
from .db import metadata


rucs = sqlalchemy.Table(
    "ruc",
    metadata,
    sqlalchemy.Column("ruc", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("razonsocial", sqlalchemy.String)
)

class Ruc:
    @staticmethod
    async def retreive(db, ruc):
        return await db.fetch_one(rucs.select().where(rucs.c.ruc==ruc))
