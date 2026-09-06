import io
import pytest


@pytest.mark.asyncio
async def test_quiz_and_tutor_integration(client, register_payload):
    # register
    r = await client.post('/api/v1/auth/register', json=register_payload)
    assert r.status_code == 200
    token = r.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # create a note and generate flashcards
    payload = {'title': 'Quiz Note', 'content': 'Alpha. Beta. Gamma. Delta.'}
    n = await client.post('/api/v1/notes/', json=payload, headers=headers)
    assert n.status_code == 200
    nid = n.json()['data']['id']
    gen = await client.post('/api/v1/flashcards/generate/from-note', json={'note_id': nid, 'count': 4}, headers=headers)
    assert gen.status_code == 200

    # generate quiz from flashcards
    q = await client.post('/api/v1/quizzes/generate/from-flashcards', headers=headers)
    assert q.status_code == 200
    quiz_id = q.json()['data']['quiz_id']

    # get quiz
    g = await client.get(f'/api/v1/quizzes/{quiz_id}', headers=headers)
    assert g.status_code == 200
    questions = g.json()['data']['questions']
    assert len(questions) >= 1

    # submit answers (all correct using answer field)
    answers = [{'question_id': questions[0]['id'], 'answer': questions[0]['answer']}]
    sub = await client.post(f'/api/v1/quizzes/{quiz_id}/submit', json={'answers': answers}, headers=headers)
    assert sub.status_code == 200
    assert sub.json()['data']['score'] >= 0

    # tutor ask (should return something)
    t = await client.post('/api/v1/tutor/ask', json={'question': 'What is this note about?'}, headers=headers)
    assert t.status_code == 200
    assert 'answer' in t.json()['data']
