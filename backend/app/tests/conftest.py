from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from supabase import Client

from app.core.config import settings
from app.core.db import init_db, get_supabase_client
from app.main import app
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def supabase_client() -> Generator[Client, None, None]:
    """Initialize Supabase client for tests."""
    init_db()
    client = get_supabase_client()
    yield client
    # Cleanup is handled by Supabase RLS policies


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, supabase_client: Client) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, supabase_client=supabase_client
    )
