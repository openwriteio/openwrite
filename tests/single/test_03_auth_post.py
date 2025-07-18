from io import BytesIO
from PIL import Image

def test_post_login(client):
    """
    Test login
    """
    resp = client.post("/login", data={
        "username":"admin",
        "password":"openwrite"
    })

    assert resp.status_code == 302
    
def test_add_post(client):
    """
    Test add new post
    """
    post = client.post("/dashboard/post/default", data={
        "title": "test",
        "content_raw": "test",
        "content": "<p>test</p>",
        "author":"1",
        "feed": "0"
    })

    assert post.status_code == 302

    post2 = client.post("/dashboard/post/default", data={   
        "title": "test",
        "content_raw": "test2",
        "content": "<p>test2</p>",
        "author": "1",
        "feed": "0"
    })

    assert post2.status_code == 302

    post3 = client.post("/dashboard/post/default", data={
        "title": "this is a test",
        "content_raw": "test",
        "content": "<p>test</p>",
        "author": "1",
        "feed": "0"
    })

    assert post3.status_code == 302
    
def test_get_post2(client):
    """
    Test newly added post
    it should have url test-2 since test was already there
    """
    check_post = client.get("/p/test-2")
    assert check_post.status_code == 200
    assert b"test2" in check_post.data

def test_edit_blog(client):
    """
    Test edit blog
    """
    blog = client.post("/dashboard/edit/default", data={
        "title":"edited_title",
        "css": "h1 { color: #deadbe; }",
        "icon": "😍",
        "theme": "warmnight"
    })

    assert blog.status_code == 200

def test_add_page(client):
    """
    Test add new page
    """
    page = client.post("/dashboard/page/default", data={
        "name": "test page",
        "url": "/test-page",
        "content_raw": "test page content",
        "content": "<p>test page content</p>",
        "show": "1"
    })

    assert page.status_code == 302

def test_add_page2(client):
    """
    Test add new page
    """
    page = client.post("/dashboard/page/default", data={
        "name": "qwerty",
        "url": "/qwerty",
        "content_raw": "test page content",
        "content": "<p>test page content</p>",
        "show": "0"
    })

    assert page.status_code == 302

def test_get_blog(client):
    """
    Test edited blog
    """
    check_blog = client.get("/")
    assert check_blog.status_code == 200
    assert b"edited_title" in check_blog.data
    assert b"deadbe" in check_blog.data
    assert b"/p/test-page" in check_blog.data
    assert b"warmnight" in check_blog.data
    assert b"/p/qwerty" not in check_blog.data

def test_get_page(client):
    """
    Test newly added page
    it should have url /test-page
    """
    check_page = client.get("/p/test-page")
    assert check_page.status_code == 200
    assert b"test page content" in check_page.data

def test_upload(client):
    """
    Test upload image
    """
    img_io = BytesIO()
    image = Image.new("RGB", (10, 10), color="red")
    image.save(img_io, "PNG")
    img_io.name = "test.png"
    img_io.seek(0)

    data = {
        'file': (img_io, 'test.png')
    }

    upload = client.post("/upload_image", data=data, content_type="multipart/form-data")
    assert upload.status_code == 200
    assert b"url" in upload.data

def test_fake_upload(client):
    """
    Test non-image upload
    """
    fake = BytesIO(b"t\x89PNG\r\n\x1a\n...totally not an image")
    fake.name = "test.png"

    data = {
        'file': (fake, "test.png")
    }

    fake_upload = client.post("/upload_image", data=data, content_type="multipart/form-data")
    assert fake_upload.status_code == 400
    assert b"not a valid image" in fake_upload.data
