import os
import sqlalchemy

from databases import Database


db = Database(os.environ.get("DATABASE_URL", "sqlite:///./data/ruc.db"))
metadata = sqlalchemy.MetaData()

db_1 = Database(os.environ.get("DATABASE_URL", "sqlite:///./data/personas.db"))
metadata_1 = sqlalchemy.MetaData()
