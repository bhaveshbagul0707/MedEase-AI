import io
import pytest


@pytest.mark.asyncio
async def test_flashcards_crud_and_integration(client, register_payload):
    # register and upload a text-based pdf
    r = await client.post('/api/v1/auth/register', json=register_payload)
    assert r.status_code == 200
    token = r.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    content = b"This is a short medical note about the heart. The heart pumps blood. Clinical relevance: know chambers."
    files = {'file': ('cardio.pdf', io.BytesIO(content), 'application/pdf')}
    resp = await client.post('/api/v1/files/upload', headers=headers, files=files)
    assert resp.status_code == 200
    fid = resp.json()['data']['id']

    # ensure processing created chunks by querying via API
    ch = await client.get(f'/api/v1/knowledge/files/{fid}/chunks', headers=headers)
    assert ch.status_code == 200
    items = ch.json()['items']
    assert len(items) > 0
    chunk_id = items[0]['id']

    # create flashcard from chunk
    payload = {'chunk_id': chunk_id}
    fc = await client.post('/api/v1/flashcards/from-chunk', json=payload, headers=headers)
    assert fc.status_code == 200
    fcid = fc.json()['data']['id']

    # get flashcard
    g = await client.get(f'/api/v1/flashcards/{fcid}', headers=headers)
    assert g.status_code == 200
    assert g.json()['data']['id'] == fcid

    # update flashcard
    up = await client.put(f'/api/v1/flashcards/{fcid}', json={'front': 'Updated Q?'}, headers=headers)
    assert up.status_code == 200
    assert up.json()['data']['front'] == 'Updated Q?'

    # review flashcard (correct)
    rv = await client.post(f'/api/v1/flashcards/{fcid}/review', json={'correct': True}, headers=headers)
    assert rv.status_code == 200
    assert rv.json()['data']['is_learned'] is True

    # list flashcards
    lst = await client.get('/api/v1/flashcards/', headers=headers)
    assert lst.status_code == 200
    assert lst.json()['data']['total'] >= 1

    # delete flashcard
    d = await client.delete(f'/api/v1/flashcards/{fcid}', headers=headers)
    assert d.status_code == 200

    # ensure gone
    g2 = await client.get(f'/api/v1/flashcards/{fcid}', headers=headers)
    assert g2.status_code == 404
