import pytest

from httpx import ASGITransport, AsyncClient

from app.main import app

async def test_health(client):
    response = await client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

async def test_create_task(client):
    response = await client.post(
        '/tasks',
        json = {'title': 'buy milk', 'description': '2 liters'},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['title'] == 'buy milk'
    assert body['description'] == '2 liters'
    assert body['done'] is False
    assert isinstance(body['id'], int)

@pytest.mark.parametrize(
    "payload",
    [
        {'title': ""},
        {"description": "no title"},
        {"title": "x" * 300},
        {},
    ],
)
async def test_create_task_invalid(client, payload):
    response = await client.post(
        '/tasks',
        json = payload
    )
    assert response.status_code == 422

async def test_list_empty(client):
    response = await client.get('/tasks')
    assert response.status_code == 200
    assert response.json() == []

async def test_list_after_create(client):
    await client.post('/tasks', json = {"title": "task 1"})
    await client.post('/tasks', json = {"title": "task 2"})
    response = await client.get('/tasks')
    assert response.status_code == 200
    titles = [t['title'] for t in response.json()]
    assert titles == ['task 1', 'task 2']

async def test_get_by_id(client, sample_task):
    response = await client.get(f'/tasks/{sample_task}')
    assert response.status_code == 200
    assert response.json()['title'] == 'one task'

async def test_get_not_found(client):
    result = await client.get('/tasks/999')
    assert result.status_code == 404
    assert result.json() == {'detail': 'task not found'}

async def test_update_toggle_done(client, sample_task):
    response = await client.patch(f'/tasks/{sample_task}', json={'done': True})
    assert response.status_code == 200
    assert response.json()['done'] is True
    assert response.json()['title'] == 'one task'

async def test_update_title_only(client, sample_task):
    response = await client.patch(f'/tasks/{sample_task}', json={"title": 'new'})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "new"
    assert body["description"] == "task description"

async def test_update_not_found(client):
    response = await client.patch("/tasks/999", json={"done": True})
    assert response.status_code == 404

async def test_delete_task(client, sample_task):
    response = await client.delete(f"/tasks/{sample_task}")
    assert response.status_code == 204
    check = await client.get(f"/tasks/{sample_task}")
    assert check.status_code == 404


async def test_delete_not_found(client):
    response = await client.delete("/tasks/999")
    assert response.status_code == 404