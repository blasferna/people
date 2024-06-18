import sqlalchemy

from databases import Database


db = Database("sqlite:///./data/ruc.db")
metadata = sqlalchemy.MetaData()

db_1 = Database("sqlite:///./data/personas.db")
metadata_1 = sqlalchemy.MetaData()
