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

def test_create_page(client):
    resp = client.post("/dashboard/page/testx", data={
        "name": "Test Page",
        "url": "/test-page",
        "content_raw": "This is a test page",
        "content": "<p>This is a test page</p>",
        "show": "1"
    })

    assert resp.status_code == 302

def test_create_unshown_page(client):
    resp = client.post("/dashboard/page/testx", data={
        "name": "Unshown Page",
        "url": "/unshown-page",
        "content_raw": "This page should not be shown",
        "content": "<p>This page should not be shown</p>",
        "show": "0"
    })

    assert resp.status_code == 302

def test_created_post(client):
    resp = client.get("/b/testx/this-is-a-test")

    assert resp.status_code == 200
    assert b"test2" in resp.data

def test_created_page(client):
    resp = client.get("/b/testx/test-page")

    assert resp.status_code == 200
    assert b"This is a test page" in resp.data

def test_unshown_page(client):
    resp = client.get("/b/testx")

    assert resp.status_code == 200
    assert b"Unshown Page" not in resp.data
    assert b"/b/testx/test-page" in resp.data

def test_update_blog(client):
    blog = client.post("/dashboard/edit/testx", data={
        "title": "edited_title",
        "css": "h1 { color: #deadbe; }",
        "icon": "",
        "theme": "warmnight"
    })

    assert blog.status_code == 200

def test_get_updated_blog(client):
    check_blog = client.get("/b/testx")
    assert check_blog.status_code == 200
    assert b"edited_title" in check_blog.data
    assert b"deadbe" in check_blog.data
    assert b"warmnight" in check_blog.data