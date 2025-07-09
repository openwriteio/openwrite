def test_register(client):
    resp = client.post("/register", data={
        "username": "test",
        "password": "test123",
        "password2": "test123"
    })

    assert resp.status_code == 200
    assert b"successful" in resp.data

def test_login(client):
    resp = client.post("/login", data={
        "username": "test",
        "password": "test123"
    })

    assert resp.status_code == 302

