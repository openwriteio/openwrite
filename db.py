from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import json

load_dotenv()

pwd = os.path.dirname(os.path.realpath(__file__))

DB_TYPE = os.getenv("DB_TYPE")
DB_PATH = os.getenv("DB_PATH")

if DB_TYPE == "sqlite":
    DB_URL = f"sqlite:///{os.path.join(pwd, DB_PATH)}"
elif DB_TYPE == "mysql":
    DB_URL = DB_PATH
else:
    raise ValueError("Unsupported DB_TYPE. Use 'sqlite' or 'mysql'.")


engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
