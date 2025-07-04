from flask import Blueprint, render_template, redirect, request, g, Response, abort
from openwrite.utils.models import Blog, Post, User, View, Like
from openwrite.utils.helpers import gen_link, sanitize_html, anonymize, get_ip
from feedgen.feed import FeedGenerator
from sqlalchemy import desc
import os
from bs4 import BeautifulSoup
from datetime import timezone, datetime

blog_bp = Blueprint("blog", __name__)

@blog_bp.route("/b/<blog>")
def show_blog(blog):
    if g.mode == "single":
        return redirect("/")
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect("/")

    if blog.access == "domain":
        return redirect(f"https://{blog.name}.{os.getenv('DOMAIN')}/")

    posts = g.db.query(Post).filter_by(blog=blog.id).order_by(desc(Post.id)).all()
    blog.url = f"/b/{blog.name}"

    return render_template("blog.html", blog=blog, posts=posts)

@blog_bp.route("/", subdomain="<blog>")
def show_subblog(blog):
    if g.mode == "single":
        return redirect("/")
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect(f"https://{os.getenv('DOMAIN')}/")

    if blog.access == "path":
        return redirect(f"https://{os.getenv('DOMAIN')}/b/{blog.name}")

    posts = g.db.query(Post).filter_by(blog=blog.id).order_by(desc(Post.id)).all()

    return render_template("blog.html", blog=blog, posts=posts)

@blog_bp.route("/b/<blog>/<post>")
def show_post(blog, post):
    if g.mode == "single":
        return redirect("/")
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect("/")

    if post == "rss":
        return _generate_rss(blog)

    if blog.access == "domain":
        return redirect(f"https://{blog.name}.{os.getenv('DOMAIN')}/{post}")

    one_post = g.db.query(Post).filter(Post.blog == blog.id, Post.link == post).first()
    if not one_post:
        return redirect("/")

    post_author = g.db.query(User).filter_by(id=blog.owner).first()
    one_post.authorname = post_author.username
    blog.url = f"/b/{blog.name}"

    ip = anonymize(get_ip())
    v = g.db.query(View).filter(View.blog == blog.id, View.post == one_post.id, View.hash == ip).count()
    user_agent = request.headers.get('User-Agent')
    if v < 1:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        new_view = View(blog=blog.id, post=one_post.id, hash=ip, date=now, agent=user_agent)
        g.db.add(new_view)
        g.db.commit()
    likes = g.db.query(Like).filter(Like.blog == blog.id, Like.post == one_post.id).count()
    one_post.likes = likes
    liked = g.db.query(Like).filter(Like.blog == blog.id, Like.post == one_post.id, Like.hash == anonymize(get_ip())).count()
    one_post.liked = liked

    user = g.db.query(User).filter_by(id=g.user) if g.user else None
    return render_template("post.html", blog=blog, post=one_post, user=user, views=v, likes=likes)

@blog_bp.route("/<post>", subdomain="<blog>")
def show_subpost(blog, post):
    if g.mode == "single":
        return redirect("/")
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect(f"https://{os.getenv('DOMAIN')}/")

    if post == "rss":
        return _generate_rss(blog)

    if blog.access == "path":
        return redirect(f"https://{os.getenv('DOMAIN')}/b/{blog.name}/{post}")

    one_post = g.db.query(Post).filter(Post.blog == blog.id, Post.link == post).first()
    if not one_post:
        return redirect("/")

    post_author = g.db.query(User).filter_by(id=blog.owner).first()
    one_post.authorname = post_author.username
    blog.url = f"https://{blog.name}.{os.getenv('DOMAIN')}"

    ip = anonymize(get_ip())
    v = g.db.query(View).filter(View.blog == blog.id, View.post == one_post.id, View.hash == ip).count()
    user_agent = request.headers.get('User-Agent')
    if v < 1:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        new_view = View(blog=blog.id, post=one_post.id, hash=ip, date=now, agent=user_agent)
        g.db.add(new_view)
        g.db.commit()

    likes = g.db.query(Like).filter(Like.blog == blog.id, Like.post == one_post.id).count()
    one_post.likes = likes
    liked = g.db.query(Like).filter(Like.blog == blog.id, Like.post == one_post.id, Like.hash == anonymize(get_ip())).count()
    one_post.liked = liked

    user = g.db.query(User).filter_by(id=g.user) if g.user else None
    return render_template("post.html", blog=blog, post=one_post, user=user, views=v)

@blog_bp.route("/p/<post>")
def single_showpost(post):
    if g.mode == "multi":
        return redirect("/")

    blog = g.db.query(Blog).filter_by(id=1).first()
    one_post = g.db.query(Post).filter(Post.blog == 1, Post.link == post).first()
    if not one_post:
        return redirect("/")

    post_author = g.db.query(User).filter_by(id=1).first()
    one_post.authorname = post_author.username

    ip = anonymize(get_ip())
    v = g.db.query(View).filter(View.blog == 1, View.post == one_post.id, View.hash == ip).count()
    user_agent = request.headers.get('User-Agent')
    if v < 1:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        new_view = View(blog=1, post=one_post.id, hash=ip, date=now, agent=user_agent)
        g.db.add(new_view)
        g.db.commit()

    likes = g.db.query(Like).filter(Like.blog == 1, Like.post == one_post.id).count()
    one_post.likes = likes
    liked = g.db.query(Like).filter(Like.blog == 1, Like.post == one_post.id, Like.hash == anonymize(get_ip())).count()
    one_post.liked = liked

    user = g.db.query(User).filter_by(id=g.user) if g.user else None
    return render_template("post.html", blog=blog, post=one_post, user=user, views=v)

@blog_bp.route("/rss")
def single_rss():
    if g.mode == "multi":
        return redirect("/")

    blog = g.db.query(Blog).first()
    return _generate_rss(blog)

@blog_bp.route("/like", methods=["POST"])
def like():
    data = request.get_json()
    if not data:
        abort(400)
    
    blog_id = data.get("blog")
    post_id = data.get("post")
    post = g.db.query(Post).filter(Post.blog == blog_id, Post.id == post_id).count()
    if post < 1:
        resp = {"status": "no_post"}
        return resp, 404
    ip = anonymize(get_ip())

    l = g.db.query(Like).filter(Like.blog == blog_id, Like.post == post_id, Like.hash == ip).first()
    if l:
        g.db.delete(l)
        g.db.commit()
        resp = {"status": "deleted"}
        status = 204
    else:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        like = Like(blog=blog_id, post=post_id, hash=ip, date=now)
        g.db.add(like)
        g.db.commit()
        resp = {"status": "ok"}
        status = 201
    return resp, status
    

def _generate_rss(blog):
    posts = g.db.query(Post).filter_by(blog=blog.id).all()
    fg = FeedGenerator()
    fg.title(blog.title)
    fg.link(href=f"https://{os.getenv('DOMAIN')}/b/{blog.name}", rel="alternate")
    fg.description(blog.description_html)

    for p in posts:
        soup = BeautifulSoup(p.content_html, "html.parser")
        fe = fg.add_entry()
        fe.title(p.title)
        fe.link(href=f"https://{os.getenv('DOMAIN')}/b/{blog.name}/{p.link}")
        fe.description(soup.get_text())
        fe.published(p.date.replace(tzinfo=timezone.utc))

    return Response(fg.rss_str(pretty=True).decode("utf-8"), mimetype="application/rss+xml")


