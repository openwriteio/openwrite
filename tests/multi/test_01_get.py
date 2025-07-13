def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"quiet" in response.data

def test_register(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"register on" in response.data

def test_login(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data

def test_discover(client):
    response = client.get("/discover")
    assert response.status_code == 200
    assert b"recent posts" in response.data
