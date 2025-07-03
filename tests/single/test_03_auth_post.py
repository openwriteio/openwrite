def test_post_flow(client):
    resp = client.post("/login", data={
        "username":"admin",
        "password":"admin123"
    })

    assert resp.status_code == 302
    
    post = client.post("/dashboard/post/default", data={
        "title": "test",
        "content_raw": "test2",
        "content": "<p>test2</p>",
        "author":"1",
        "feed": "0"
    })

    assert post.status_code == 302
    
    check_post = client.get("/p/test-2")
    assert check_post.status_code == 200
    assert b"test2" in check_post.data

    blog = client.post("/dashboard/edit/default", data={
        "title":"edited_title",
        "description_raw":"edited_description",
        "description_html":"<p>edited_description</p>",
        "css": "h1 { color: #deadbe; }",
        "theme": "warmnight"
    })

    assert blog.status_code == 200
    
    check_blog = client.get("/")
    assert check_blog.status_code == 200
    assert b"edited_title" in check_blog.data
    assert b"edited_description" in check_blog.data
    assert b"deadbe" in check_blog.data
    assert b"warmnight" in check_blog.data
