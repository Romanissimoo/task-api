import pytest_asyncio

from httpx import ASGITransport, AsyncClient

from main import app, tasks

@pytest_asyncio.fixture
async def client():
    #Очищаем словарь перед тестами
    tasks.clear()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as c:
        yield c