def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"hello" in response.data

def test_post(client):
    response = client.get("/p/test")
    assert response.status_code == 200
    assert b"this" in response.data
    assert b"by admin" in response.data

def test_rss(client):
    response = client.get("/rss")
    assert response.status_code == 200
    assert b"<channel>" in response.data
