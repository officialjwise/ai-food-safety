import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AI Food Safety Platform API"}

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Test User",
                "role": "consumer"
            },
        )
    # Note: This might fail if DB is not set up in test env, 
    # but demonstrates the test structure.
    # In a real scenario, we'd mock the DB or use a test DB.
    assert response.status_code in [200, 400] # 400 if user exists
