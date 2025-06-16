from flask import Blueprint, render_template, redirect, request, g
from openwrite.utils.models import Blog, Post, User, View
from openwrite.utils.helpers import sanitize_html, gen_link, safe_css, send_create_activity

from sqlalchemy import desc
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json

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
    if g.user is None:
        return redirect("/login")

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

    try:
        new_blog = Blog(
            owner=g.user,
            title=form_name,
            name=form_url,
            index=form_index,
            access=form_access,
            description_raw="![hello](https://openwrite.b-cdn.net/hello.jpg =500x258)\n\n# Hello there! 👋",
            description_html="<p><img src=\"https://openwrite.b-cdn.net/hello.jpg\" width=\"500\" height=\"258\"></p><h1>Hello there! 👋</h1>",
            css="",
            pub_key=public_pem,
            priv_key=private_pem
        )
        g.db.add(new_blog)
        g.db.commit()
        return redirect("/dashboard")
    except Exception:
        return render_template("create.html", error=g.trans['error'])

@dashboard_bp.route("/dashboard/delete/<name>")
def delete_blog(name):
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

    if request.method == "GET":
        return render_template("edit.html", blog=blog, posts=posts)

    blog.description_raw = request.form.get("description_raw")
    blog.description_html = sanitize_html(request.form.get("description_html"))
    if len(request.form.get("title")) > 30:
        return render_template("edit.html", blog=blog, posts=posts, error="Title too long! Max 30 characters.")
    blog.css = safe_css(request.form.get("css"))
        
    blog.title = request.form.get("title")
    g.db.commit()

    return render_template("edit.html", blog=blog, posts=posts)

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
    dupes = g.db.query(Post).filter(Post.link.startswith(link), Post.blog == blog.id).count()
    if dupes > 0:
        link += f"-{dupes + 1}"

    now = datetime.now(timezone.utc)
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
    if blog.followers is not None:
        followers = json.loads(blog.followers)

    for actor in followers:
        send_create_activity(
            f"https://{g.main_domain}/activity/{blog.name}",
            blog.priv_key,
            url,
            followers,
            f"<p>{title}</p><a href=\"{url}\">{url}</a>",
            actor
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
        'date': request.form.get('date'),
        'author_name': u.username
    }

    return render_template("preview.html", data=data)

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
    dupes = g.db.query(Post).filter(Post.link.startswith(link), Post.blog == blog_obj.id).count()
    if dupes > 0 and link != post:
        link += f"-{dupes + 1}"

    p.title = title
    p.content_raw = request.form.get("content_raw")
    p.content_html = sanitize_html(request.form.get("content"))
    p.author = request.form.get("author")
    p.link = link
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

