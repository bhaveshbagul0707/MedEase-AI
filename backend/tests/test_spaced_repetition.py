import io
import pytest


@pytest.mark.asyncio
async def test_spaced_repetition_flow(client, register_payload):
    r = await client.post('/api/v1/auth/register', json=register_payload)
    assert r.status_code == 200
    token = r.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # create a note and generate a flashcard
    payload = {'title': 'Test Note', 'content': 'First sentence. Second sentence. Third.'}
    n = await client.post('/api/v1/notes/', json=payload, headers=headers)
    assert n.status_code == 200
    nid = n.json()['data']['id']

    # generate flashcards from note
    gen = await client.post('/api/v1/flashcards/generate/from-note', json={'note_id': nid, 'count': 2}, headers=headers)
    assert gen.status_code == 200
    items = gen.json()['data']
    assert len(items) >= 1

    # list due reviews (should be due immediately)
    due = await client.get('/api/v1/reviews/due', headers=headers)
    assert due.status_code == 200
    assert len(due.json()['data']) >= 1
    fid = due.json()['data'][0]['id']

    # submit incorrect answer
    sub = await client.post(f'/api/v1/reviews/{fid}/answer', json={'correct': False}, headers=headers)
    assert sub.status_code == 200

    # submit correct answer
    sub2 = await client.post(f'/api/v1/reviews/{fid}/answer', json={'correct': True}, headers=headers)
    assert sub2.status_code == 200
