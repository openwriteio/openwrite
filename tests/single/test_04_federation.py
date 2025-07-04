def test_openwrite(client):
    resp = client.get("/.well-known/openwrite")
    assert resp.status_code == 200
    assert b"uptime" in resp.data

def test_getperson(client):
    resp = client.get("/.well-known/webfinger?resource=acct:default@singletest.open.write")
    assert resp.status_code == 200
    assert b"subject" in resp.data

def test_getinfo(client):
    resp = client.get("/activity/default")
    assert resp.status_code == 200
    assert b"outbox" in resp.data

def test_outbox(client):
    resp = client.get("/outbox/default?page=1")
    assert resp.status_code == 200
    assert b"this is a test" in resp.data
