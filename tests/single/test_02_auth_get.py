def test_get_flow(client):
    resp = client.post("/login", data={
        "username": "admin",
        "password": "admin123"
    })

    assert resp.status_code == 302

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"your blog" in dashboard.data

    edit = client.get("/dashboard/edit/default")
    assert edit.status_code == 200
    assert b"Title:" in edit.data

    new_post = client.get("/dashboard/post/default")
    assert new_post.status_code == 200
    assert b"Include author" in new_post.data

    edit_post = client.get("/dashboard/edit/default/test")
    assert edit_post.status_code == 200
    assert b"Include author" in edit_post.data
