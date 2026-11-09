import pytest_asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app, tasks

@pytest_asyncio.fixture
async def client():
    #Очищаем словарь перед тестами
    tasks.clear()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as c:
        yield c

@pytest_asyncio.fixture
async def sample_task(client):
    create = await client.post('/tasks', json={'title':"one task", 'description': "task description"})
    task_id = create.json()['id']
    return task_id