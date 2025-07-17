from flask import Blueprint, render_template, redirect, request, g, abort
from openwrite.utils.models import Blog, Post, User, View, Page
from openwrite.utils.helpers import sanitize_html, gen_link, safe_css, send_activity, is_html, get_themes
import requests
from sqlalchemy import desc
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json
import bcrypt
import markdown
from bs4 import BeautifulSoup
from user_agents import parse
import re

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if g.user is None:
        return redirect("/login")

    user_blogs = g.db.query(Blog).filter_by(owner=g.user).all()
    user = g.db.query(User).filter_by(id=g.user)

    return render_template("dashboard.html", blogs=user_blogs, user=user)

@dashboard_bp.route("/dashboard/create", methods=['GET', 'POST'])
def create_blog():
    if g.mode == "single":
        return redirect("/")
    if g.user is None:
        return redirect("/login")

    if int(g.blog_limit) > 0:
        count = g.db.query(Blog).filter_by(owner=g.user).count()
        if count >= int(g.blog_limit):
            return render_template("create.html", error="Blog limit reached!")

    if request.method == "GET":
        return render_template("create.html")

    form_name = request.form.get("name")
    form_url = gen_link(request.form.get("url"))
    if len(form_name) > 30:
        return render_template("create.html", error="Title too long! Max 30 characters.")
    if len(form_url) > 30:
        return render_template("create.html", error="URL too long! Max 30 characters.")
    blog = g.db.query(Blog).filter_by(name=form_url).first()
    if blog:
        return render_template("create.html", error="This URL already exists!")
    
    form_index = request.form.get("index") or "off"
    form_access = request.form.get("access")
    if form_access not in ("path", "domain"):
        return render_template("create.html", error="Wrong access!")
    
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        new_blog = Blog(
            owner=g.user,
            title=form_name,
            name=form_url,
            index=form_index,
            access=form_access,
            css="",
            description_raw="x",
            description_html="x",
            pub_key=public_pem,
            priv_key=private_pem,
            theme="default",
            favicon="",
            created=now
        )
        g.db.add(new_blog)
        g.db.commit()

        b_id = g.db.query(Blog).filter_by(name=form_url).first().id

        new_page = Page(
            blog=b_id,
            name="Home",
            url="",
            content_raw=f"![hello](https://openwrite.b-cdn.net/hello.jpg =500x258)\n\n# Hello there! 👋\n\nYou can edit your blog home page in [dashboard](https://{g.main_domain}/dashboard/edit/{form_url})\n\n---\n### Posts\n\n{{posts}}",
            content_html=f"<p><img src=\"https://openwrite.b-cdn.net/hello.jpg\" width=\"500\" height=\"258\"></p><h1>Hello there! 👋</h1><p>You can edit your blog home page in <a href=\"https://{g.main_domain}/dashboard/edit/{form_url}\">dashboard</a></p>\n\n<hr>\n<h3>Posts\n\n{{posts}}",
            show="off"
        )
        g.db.add(new_page)
        g.db.commit()
           
        return redirect("/dashboard")
    except Exception:
        return render_template("create.html", error=g.trans['error'])

@dashboard_bp.route("/dashboard/delete/<name>")
def delete_blog(name):
    if g.mode == "single":
        return redirect("/")
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None or blog.owner != g.user:
        return redirect("/dashboard")

    g.db.delete(blog)
    g.db.commit()
    return redirect("/dashboard")

@dashboard_bp.route("/dashboard/edit/<name>", methods=['GET', 'POST'])
def edit_blog(name):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None or blog.owner != g.user:
        return redirect("/dashboard")

    posts = g.db.query(Post).filter_by(blog=blog.id).all()
    for p in posts:
        v = g.db.query(View).filter(View.post == p.id, View.blog == blog.id).count()
        p.views = v

    pages = g.db.query(Page).filter_by(blog=blog.id).all()

    themes = get_themes()
    themes.append("default")

    if request.method == "GET":
        return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    if len(request.form.get("title")) > 30:
        return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages, error="Title too long! Max 30 characters.")
    blog.css = safe_css(request.form.get("css"))
    blog.updated = now   
    blog.title = request.form.get("title")
    blog.favicon = request.form.get("icon")[:10]
    selected_theme = request.form.get("theme")
    if selected_theme not in themes:
        return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages, error="Wrong theme!")
    blog.theme = selected_theme
    g.db.commit()

    return render_template("edit.html", blog=blog, posts=posts, themes=themes, pages=pages)

@dashboard_bp.route("/dashboard/post/<name>", methods=['GET', 'POST'])
def new_post(name):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None or blog.owner != g.user:
        return redirect("/dashboard")

    if request.method == "GET":
        return render_template("new_post.html", blog=blog)

    u = g.db.query(User).filter_by(id=g.user).first()
    title = request.form.get('title')
    if len(title) > 120:
        return render_template("new_post.html", blog=blog, error="Title too long! Max 120 characters.")
        
    link = gen_link(title)
    if link == "rss":
        link = "p_rss"
    dupes_posts = g.db.query(Post).filter(Post.link.startswith(link), Post.blog == blog.id).count()
    dupes_pages = g.db.query(Page).filter(Page.url == link, Page.blog == blog.id).count()
    dupes = dupes_posts + dupes_pages
    if dupes > 0:
        link += f"-{dupes + 1}"

    now = datetime.now(timezone.utc).replace(microsecond=0)
    date = now

    post = Post(
        blog=blog.id,
        title=title,
        content_raw=request.form.get('content_raw'),
        content_html=sanitize_html(request.form.get('content')),
        author=request.form.get('author'),
        link=link,
        date=now,
        feed=request.form.get('feed')
    )
    g.db.add(post)
    g.db.commit()
    
    if blog.access == "domain":
        url = f"https://{blog.name}.openwrite.io/{link}"
    else:
        url = f"https://openwrite.io/b/{blog.name}/{link}"

    followers = []
    if blog.followers not in (None, "null", "NULL"):
        followers = json.loads(blog.followers)

    for actor in followers:
        now = datetime.utcnow().isoformat() + "Z"
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"{url}",
            "type": "Create",
            "actor": f"https://{g.main_domain}/activity/{blog.name}",
            "cc": followers,
            "object": {
                "id": f"{url}",
                "type": "Note",
                "published": now,
                "attributedTo": f"https://{g.main_domain}/activity/{blog.name}",
                "content": f"<p>{title}</p><a href=\"{url}\">{url}</a>",
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": followers
            },
            "to": ["https://www.w3.org/ns/activitystreams#Public"]
        }       
        send_activity(
            activity,
            blog.priv_key,
            f"https://{g.main_domain}/activity/{blog.name}",
            f"{actor}/inbox"
        )
        
    return redirect(f"/dashboard/edit/{blog.name}")

@dashboard_bp.route("/dashboard/preview", methods=['POST'])
def preview():
    if g.user is None:
        return redirect("/login")

    u = g.db.query(User).filter_by(id=g.user).first()
    data = {
        'title': request.form.get('title'),
        'content': sanitize_html(request.form.get('content')),
        'author': request.form.get('author'),
        'blog_title': request.form.get('blog_title'),
        'blog_name': request.form.get('blog_name'),
        'theme': request.form.get('theme'),
        'date': request.form.get('date'),
        'author_name': u.username
    }

    return render_template("preview.html", data=data)

@dashboard_bp.route("/dashboard/blog_preview", methods=['POST'])
def blog_preview():
    if g.user is None:
        return redirect("/login")

    u = g.db.query(User).filter_by(id=g.user).first()
    blog_name = request.referrer.split("/")[-1]
    blog = g.db.query(Blog).filter_by(name=blog_name).first()
    if not blog:
        return redirect("/")

    homepage = g.db.query(Page).filter(Page.blog == blog.id, Page.url == "").first()
    data = {
        'title': request.form.get('title'),
        'css': request.form.get('css'),
        'icon': request.form.get('icon'),
        'content': homepage.content_html,
        'theme': request.form.get('theme')
    }


    return render_template("blog_preview.html", data=data)

@dashboard_bp.route("/dashboard/edit/<blog>/<post>", methods=['GET', 'POST'])
def edit_post(blog, post):
    if g.user is None:
        return redirect("/login")

    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None or blog_obj.owner != g.user:
        return redirect("/dashboard")

    e_post = g.db.query(Post).filter_by(link=post).first()
    if request.method == "GET":
        return render_template("new_post.html", blog=blog_obj, post=e_post)

    p = g.db.query(Post).filter_by(link=post, blog=blog_obj.id).first()
    if not p:
        return redirect("/dashboard")

    title = request.form.get("title")
    if len(title) > 120:
        return render_template("new_post.html", blog=blog_obj, error="Title too long! Max 120 characters.")
    link = gen_link(title)
    if link == "rss":
        link = "p_rss"
    dupes_posts = g.db.query(Post).filter(Post.link.startswith(link), Post.blog == blog_obj.id).count()
    dupes_pages = g.db.query(Page).filter(Page.url == link, Page.blog == blog_obj.id).count()
    dupes = dupes_posts + dupes_pages
    if dupes > 0 and link != post:
        link += f"-{dupes + 1}"

    p.title = title
    now = datetime.now(timezone.utc).replace(microsecond=0)
    p.content_raw = request.form.get("content_raw")
    p.content_html = sanitize_html(request.form.get("content"))
    p.author = request.form.get("author")
    p.feed = request.form.get("feed")
    p.link = link
    p.updated = now
    g.db.commit()
    return redirect(f"/dashboard/edit/{blog_obj.name}")

@dashboard_bp.route("/dashboard/edit/<blog>/<post>/delete")
def delete_post(blog, post):
    if g.user is None:
        return redirect("/login")

    blog_obj = g.db.query(Blog).filter_by(name=blog).first()
    if blog_obj is None or blog_obj.owner != g.user:
        return redirect("/dashboard")

    p = g.db.query(Post).filter_by(link=post, blog=blog_obj.id).first()
    if p:
        g.db.delete(p)
        g.db.commit()

    return redirect(f"/dashboard/edit/{blog_obj.name}")


@dashboard_bp.route("/dashboard/changepw", methods=['GET', 'POST'])
def changepw():
    if g.user is None:
        return redirect("/login")

    if request.method == "GET":
       return render_template("changepw.html")

    old_pw = request.form.get("current_pass")
    new_pass = request.form.get("new_pass")
    new_pass2 = request.form.get("new_pass2")
    user = g.db.query(User).filter_by(id=g.user).first()
    if user and bcrypt.checkpw(old_pw.encode('utf-8'), user.password_hash.encode('utf-8')):
        if new_pass != new_pass2:
            return render_template("changepw.html", error=g.trans['passwords_dont_match'])
        hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = hashed
        return redirect("/dashboard")

    else:
        return render_template("changepw.html", error=g.trans['invalid_password'])
        

@dashboard_bp.route("/dashboard/import", methods=['GET', 'POST'])
def migrate():
    if g.user is None:
        return redirect("/login")

    blogs = g.db.query(Blog).filter_by(owner=g.user).all()
    if request.method == "GET":
       return render_template("import.html", blogs=blogs)

    data = request.get_json()
    posts = data.get("posts")
    blog_d = data.get("blog")

    blog = g.db.query(Blog).filter_by(name=blog_d).first()
    if blog.owner != g.user:
        return redirect("/dashboard")

    for post in posts:
        title = post['title']
        content = post['content']
        date = datetime.strptime(post['date'], "%a, %d %b %Y %H:%M:%S %Z")

        if is_html(content):
            soup = BeautifulSoup(content, "html.parser")
            text_content = soup.get_text()
            html_content = content
        else:
            html_content = markdown.markdown(content)
            text_content = content
        new_post = Post(blog=blog.id, content_raw=text_content, content_html=html_content, author='0', feed='0', date=date, title=title, link=gen_link(title))
        g.db.add(new_post)
        g.db.commit()

    return "ok", 200

@dashboard_bp.route("/dashboard/stats/<blog>")
def stats(blog):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog.owner != g.user:
        return redirect("/dashboard")

    posts = g.db.query(Post).filter_by(blog=blog.id).all()

    return render_template("stats.html", blog=blog, posts=posts)

@dashboard_bp.route("/dashboard/get_stats/<blog>/<post>/<limit>")
def get_stats(blog, post, limit):
    if g.user is None:
        abort(403)

    b = g.db.query(Blog).filter_by(id=blog).first()
    if g.user != b.owner:
        abort(403)

    if int(limit) not in (24, 168, 720, 2160):
        abort(400)
    time_threshold = datetime.now() - timedelta(hours=int(limit))
    views_obj = {}
    views_obj["views"] = []
    start_from = g.db.query(View).filter(View.blog == blog, View.post == post, View.date < time_threshold).count()
    views_obj["start_from"] = start_from
    views = g.db.query(View).filter(View.blog == blog, View.post == post, View.date >= time_threshold).all()
    for v in views:
        os = "Unknown"
        browser = "Unknown"
        if v.agent not in (None, "null", "NULL"):
            ua = parse(v.agent)
            os = ua.os.family
            browser = ua.browser.family
        views_obj["views"].append([v.date, os, browser])

    return views_obj

@dashboard_bp.route("/dashboard/page/<blog>", methods=['GET', 'POST'])
def new_page(blog):
    if g.user is None:
        abort(403)
    blog = g.db.query(Blog).filter_by(name=blog).first()

    if not blog:
        abort(404)

    if blog.owner != g.user:
        abort(403)

    if request.method == "GET":
        return render_template("new_page.html", blog=blog)

    name = request.form.get("name")
    url = request.form.get("url")
    content_raw = request.form.get("content_raw")
    content_html = request.form.get("content")
    show = request.form.get("show")
    if len(name) > 120:
        return render_template("new_page.html", blog=blog, error="Name too long! Max 120 characters")
    if not re.match(r"^\/[a-zA-Z0-9\-\_]+$", url):
        return render_template("new_page.html", blog=blog, error="Invalid URL!")

    url = url[1:]
    if url == "rss":
        url = "p_rss"
    dupes_posts = g.db.query(Post).filter(Post.link.startswith(url), Post.blog == blog.id).count()
    dupes_pages = g.db.query(Page).filter(Page.url == url, Page.blog == blog.id).count()
    dupes = dupes_posts + dupes_pages
    if dupes > 0:
        url = f"{url}-{dupes + 1}"

    new_page = Page(blog=blog.id, name=name, url=url, content_raw=content_raw, content_html=sanitize_html(content_html), show=show)

    g.db.add(new_page)
    g.db.commit()
    return redirect(f"/dashboard/edit/{blog.name}")

@dashboard_bp.route("/dashboard/page/<page>/edit", methods=['GET', 'POST'])
def edit_page(page):
    if g.user is None:
        abort(403)

    page = g.db.query(Page).filter_by(id=page).first()
    if not page:
        abort(404)
    blog = g.db.query(Blog).filter_by(id=page.blog).first()

    if not blog:
        abort(404)

    if blog.owner != g.user:
        abort(403)
    home = False
    if page.url == "":
        home = True

    if request.method == 'GET':
        return render_template("new_page.html", blog=blog, page=page, home=home)

    name = request.form.get("name")
    content_raw = request.form.get("content_raw")
    content_html = request.form.get("content")
    show = request.form.get("show")
    url = request.form.get("url")
    if len(name) > 120:
        return render_template("new_page.html", blog=blog, page=page, home=home, error="Name too long!")
    if home == False:
        if not re.match(r"^\/[a-zA-Z0-9\-\_]+$", url):
            return render_template("new_page.html", blog=blog, error="Invalid URL!")

        url = url[1:]
        if url == "rss":
            url = "p_rss"
        dupes_posts = g.db.query(Post).filter(Post.link.startswith(url), Post.blog == blog.id).count()
        dupes_pages = g.db.query(Page).filter(Page.url == url, Page.blog == blog.id).count()
        dupes = dupes_posts + dupes_pages
        if dupes > 0 and url != page.url:
            url = f"{url}-{dupes + 1}"

    page.name = name
    page.content_raw = content_raw
    page.content_html = sanitize_html(content_html)
    page.show = show
    if home == False:
        page.url = url

    g.db.commit()
    return redirect(f"/dashboard/edit/{blog.name}")

@dashboard_bp.route("/dashboard/page_preview", methods=['POST'])
def page_preview():
    if g.user is None:
        return redirect("/")

    data = {
        'name': request.form.get('name'),
        'content': sanitize_html(request.form.get('content')),
        'blog_title': request.form.get('blog_title'),
        'blog_name': request.form.get('blog_name'),
        'theme': request.form.get('theme')
    }

    return render_template("page_preview.html", data=data)


@dashboard_bp.route("/dashboard/page/<page>/delete")
def page_delete(page):
    if g.user is None:
        return redirect("/")

    page = g.db.query(Page).filter_by(id=page).first()
    blog = g.db.query(Blog).filter_by(id=page.blog).first()

    if blog.owner != g.user:
        return abort(403)

    g.db.delete(page)
    g.db.commit()

    return redirect(f"/dashboard/edit/{blog.name}")
