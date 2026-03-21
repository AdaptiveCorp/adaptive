import httpx
import pytest

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture()
def client():
    """httpx client pointing at the real running API."""
    with httpx.Client(base_url=BASE_URL) as c:
        yield c
