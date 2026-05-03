"""Tests for the FastAPI API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_root(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jarvis AI Assistant"

    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestSettingsEndpoints:
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/api/settings/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestMonitoringEndpoints:
    @pytest.mark.asyncio
    async def test_system_status(self, client):
        response = await client.get("/api/monitoring/status")
        assert response.status_code == 200
        data = response.json()
        assert "cpu" in data
        assert "memory" in data

    @pytest.mark.asyncio
    async def test_cpu_info(self, client):
        response = await client.get("/api/monitoring/cpu")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_memory_info(self, client):
        response = await client.get("/api/monitoring/memory")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_process_list(self, client):
        response = await client.get("/api/monitoring/processes")
        assert response.status_code == 200
        assert "processes" in response.json()
