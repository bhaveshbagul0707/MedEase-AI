import io
import pytest


@pytest.mark.asyncio
async def test_processing_and_rag(client, register_payload):
    # register and upload a "pdf" that is just plain text
    r = await client.post('/api/v1/auth/register', json=register_payload)
    assert r.status_code == 200
    token = r.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    content = b"This is a test document about cardiology. It mentions heart, lungs, and vessels."
    files = {'file': ('test.pdf', io.BytesIO(content), 'application/pdf')}
    resp = await client.post('/api/v1/files/upload', headers=headers, files=files)
    assert resp.status_code == 200
    fid = resp.json()['data']['id']

    # After upload processing (runs inline in tests) the file should be READY
    g = await client.get(f'/api/v1/files/{fid}', headers=headers)
    assert g.status_code == 200
    assert g.json()['data']['status'] == 'READY'

    # Call chat endpoint
    q = {'question': 'What is this document about?', 'top_k': 2}
    chat = await client.post(f'/api/v1/knowledge/files/{fid}/chat', json=q, headers=headers)
    assert chat.status_code == 200
    ans = chat.json()
    assert 'cardiology' in ans['answer'] or 'heart' in ans['answer']
