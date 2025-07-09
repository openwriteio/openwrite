import pytest
from openwrite.utils.create_db import init_db
from openwrite.utils.models import User, Blog, Home, Post
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

    init_db("sqlite", db_path)
    from openwrite.utils.db import init_engine, SessionLocal
    init_engine("sqlite", db_path)
    hashed = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt())
    u1 = User(username="admin", email="", password_hash=hashed.decode("utf-8"), verified=1, admin=1)

    domain = "multitest.open.write"

    now = datetime.now(timezone.utc).replace(microsecond=0)

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
   
    home_en = Home(language="en", name="hometext", type="text", content="quiet space for loud thoughts")

    SessionLocal.add(u1)
    SessionLocal.add(home_en)
    SessionLocal.commit()

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
