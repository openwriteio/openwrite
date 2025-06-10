from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
import json

load_dotenv()

pwd = os.path.dirname(os.path.realpath(__file__))

DB_TYPE = os.getenv("DB_TYPE")
DB_PATH = os.getenv("DB_PATH")

if DB_TYPE == "sqlite":
    DB_URL = f"sqlite:///{os.path.join(pwd, DB_PATH)}"
    engine = create_engine(DB_URL, echo=False, future=True, connect_args={"check_same_thread": False}, poolclass=StaticPool)
elif DB_TYPE == "mysql":
    DB_URL = DB_PATH
    engine = create_engine(DB_URL, echo=False, future=True)
else:
    raise ValueError("Unsupported DB_TYPE. Use 'sqlite' or 'mysql'.")


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
