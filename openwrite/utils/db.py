from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
import json
from openwrite.db.base import Base

SessionLocal = None
engine = None

def init_engine(dbtype, dbpath):
    global SessionLocal, engine
    load_dotenv()

    pwd = os.path.dirname(os.path.realpath(__file__))

    if dbtype == "sqlite":
        DB_URL = f"sqlite:///{dbpath}"
        engine = create_engine(DB_URL, echo=False, future=True, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    elif dbtype == "mysql":
        DB_URL = dbpath
        engine = create_engine(DB_URL, echo=False, future=True)
    else:
        raise ValueError("Unsupported DB_TYPE. Use 'sqlite' or 'mysql'.")


    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return engine

