import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import task_storage


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    task_storage.clear()
    yield
    task_storage.clear()
