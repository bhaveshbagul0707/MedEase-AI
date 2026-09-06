import io
import pytest


@pytest.mark.asyncio
async def test_notes_crud_and_integration_with_pdf(client, register_payload):
    # register and upload a text-based pdf
    r = await client.post('/api/v1/auth/register', json=register_payload)
    assert r.status_code == 200
    token = r.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    content = b"This is a study note about anatomy. It mentions bones and muscles."
    files = {'file': ('anatomy.pdf', io.BytesIO(content), 'application/pdf')}
    resp = await client.post('/api/v1/files/upload', headers=headers, files=files)
    assert resp.status_code == 200
    fid = resp.json()['data']['id']

    # ensure processing created chunks by querying via API
    ch = await client.get(f'/api/v1/knowledge/files/{fid}/chunks', headers=headers)
    assert ch.status_code == 200
    items = ch.json()['items']
    assert len(items) > 0
    chunk_id = items[0]['id']

    # create a note linked to chunk
    payload = {'title': 'Chunk Note', 'content': 'Important point', 'file_id': fid, 'chunk_id': chunk_id}
    n = await client.post('/api/v1/notes/', json=payload, headers=headers)
    assert n.status_code == 200
    nid = n.json()['data']['id']

    # get note
    g = await client.get(f'/api/v1/notes/{nid}', headers=headers)
    assert g.status_code == 200
    assert g.json()['data']['chunk_id'] == chunk_id

    # update note
    up = await client.put(f'/api/v1/notes/{nid}', json={'content': 'Updated'}, headers=headers)
    assert up.status_code == 200
    assert up.json()['data']['content'] == 'Updated'

    # delete note
    d = await client.delete(f'/api/v1/notes/{nid}', headers=headers)
    assert d.status_code == 200

    # ensure gone
    g2 = await client.get(f'/api/v1/notes/{nid}', headers=headers)
    assert g2.status_code == 404
