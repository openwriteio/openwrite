import pytest
from openwrite import create_app
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import tempfile
import os
import bcrypt
from datetime import datetime, timezone

@pytest.fixture(scope="package")
def app():
    db_fd, db_path = tempfile.mkstemp()

    f_abs = os.path.abspath(__file__)
    cwd = "/".join(f_abs.split("/")[:-1])
    test_config = {
        "DB_TYPE": "sqlite",
        "DB_PATH": db_path,
        "env": f"{cwd}/envtest"
    }

    from openwrite.utils.db import init_engine, SessionLocal
    init_engine("sqlite", db_path)

    domain = "singletest.open.write"

    now = datetime.now(timezone.utc).replace(microsecond=0)

    app = create_app(test_config)
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test",
    })


    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope="package")
def client(app):
    return app.test_client()

@pytest.fixture(scope="package")
def runner(app):
    return app.test_cli_runner()
