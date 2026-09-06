import pytest


@pytest.mark.asyncio
async def test_study_progress_analytics(client, register_payload):
    r = await client.post('/api/v1/auth/register', json=register_payload)
    assert r.status_code == 200
    token = r.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # call analytics
    a = await client.get('/api/v1/analytics/study-progress', headers=headers)
    assert a.status_code == 200
    data = a.json()['data']
    assert 'total_flashcards' in data
    assert 'due_reviews' in data
