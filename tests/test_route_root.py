import pytest


@pytest.mark.asyncio
async def test_root(client):
    res = client.get('api/healthchecker')
    print(res.text)

    assert res.status_code == 200