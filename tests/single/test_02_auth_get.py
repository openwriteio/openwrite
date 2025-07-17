def test_login(client):
    resp = client.post("/login", data={
        "username": "admin",
        "password": "openwrite"
    })

    assert resp.status_code == 302

def test_dashboard(client):
    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"your blog" in dashboard.data

def test_edit(client):
    edit = client.get("/dashboard/edit/default")
    assert edit.status_code == 200
    assert b"Title:" in edit.data

def test_post(client):
    new_post = client.get("/dashboard/post/default")
    assert new_post.status_code == 200
    assert b"Include author" in new_post.data

def test_edit_post(client):
    edit_post = client.get("/dashboard/edit/default/test")
    assert edit_post.status_code == 200
    assert b"Include author" in edit_post.data

def test_add_page(client):
    add_page = client.get("/dashboard/page/default")
    assert add_page.status_code == 200
    assert b"URL" in add_page.data

def test_stats(client):
    stats = client.get("/dashboard/get_stats/1/1/24")
    assert stats.status_code == 200
    assert stats.content_type == "application/json"
    assert b"start_from" in stats.data
