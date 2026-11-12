import os
import sys
from pathlib import Path
import tempfile
import pytest
from cryptography.fernet import Fernet

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
TEST_DIR = tempfile.TemporaryDirectory(prefix="mizan-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(
    Path(TEST_DIR.name) / "test.db"
).replace("\\", "/")
os.environ["EVIDENCE_DIR"] = str(Path(TEST_DIR.name) / "evidence")
os.environ["EVIDENCE_KEY"] = Fernet.generate_key().decode()
os.environ["DEMO_PASSWORD"] = "test-only-generated-secret"
from app.db import Base, engine
from app.seed import seed
from app.main import app
from app.core import attempts
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    attempts.clear()
    seed()
    yield


@pytest.fixture
def client():
    with TestClient(app, headers={"X-Mizan-Request": "1"}) as c:
        yield c


def login(client, name="owner"):
    response = client.post(
        "/api/login", json={"username": name, "password": os.environ["DEMO_PASSWORD"]}
    )
    assert response.status_code == 200, response.text
    return response.json()


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    TEST_DIR.cleanup()
