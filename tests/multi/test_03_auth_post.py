def test_login(client):
    resp = client.post("/login", data={
        "username": "test",
        "password": "test123"
    })

    assert resp.status_code == 302

def test_create_blog(client):
    resp = client.post("/dashboard/create", data={
        "name": "testx",
        "url": "testx",
        "index": "off",
        "access": "path"
    })
    
    assert resp.status_code == 302

def test_created_blog(client):
    resp = client.get("/b/testx")
    assert b"Hello there" in resp.data

def test_post(client):
    post = client.post("/dashboard/post/testx", data={
        "title": "this is a test",
        "content_raw": "test2",
        "content": "<p>test2</p>",
        "author":"1",
        "feed": "0"
    })

    assert post.status_code == 302

def test_created_post(client):
    resp = client.get("/b/testx/this-is-a-test")

    assert resp.status_code == 200
    assert b"test2" in resp.data
