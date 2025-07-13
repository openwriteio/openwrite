def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"hello" in response.data

def test_rss(client):
    response = client.get("/rss")
    assert response.status_code == 200
    assert b"<channel>" in response.data

