import os, subprocess
from dotenv import load_dotenv
from openwrite.utils.db import init_engine, SessionLocal
from openwrite.utils.models import Blog, Post, User, View
from openwrite.utils.helpers import anonymize
from md2gemini import md2gemini
from datetime import datetime, timezone
session = None

def blog_index(req):
    global session
    try:
        blog = session.query(Blog).filter_by(name="default").first()
        posts = (session.query(Post)
                        .filter_by(blog=blog.id)
                        .order_by(Post.id.desc())
                        .all())
        body = f"# 📓 {blog.title}\n\n"
        body += md2gemini(blog.description_raw.replace("#", ""))
        body += "\n--------------------------------------------------\n"
        body += "### Posts:\n\n"
        for post in posts:
            body += f"=> /p/{post.link} {post.title}\n"
        return body
    finally:
        session.close()

def blog_post(req):
    global session
    path = req.path
    if len(path.split("/")) == 3:
        
        slug = path.split("/")[2]
        try:
            blog = session.query(Blog).filter_by(name="default").first()
            post = (session.query(Post)
                          .filter_by(blog=blog.id, link=slug)
                          .first())
            if not post:
                return "not found"
            user = session.query(User).filter_by(id=blog.owner).first()

            now = datetime.now(timezone.utc)
            ip = anonymize(req.remote_address[0])
            v = session.query(View).filter(View.blog==blog.id, View.post==post.id, View.hash==ip).count()
            if v < 1:
                new_view = View(blog=blog.id, post=post.id, hash=ip, date=now, agent="gemini")
                session.add(new_view)
                session.commit()

            post.authorname = user.username
            gemtext = f"=> /b/{blog.name} 📓 {blog.title}\n"
            gemtext += f"# 🧾 {post.title}\n\n"
            gemtext += f"{post.date} "
            if post.author != "0":
                gemtext += f"by {post.authorname}"
            gemtext += "\n--------------------------------------------------\n"
            gemtext += f"\n\n{md2gemini(post.content_raw)}"
            return gemtext
          
        finally:
            session.close()
            
    else:
        return "not found"

def init(capsule):
    global session
    load_dotenv()
    init_engine(os.getenv("DB_TYPE", "sqlite"),
                    os.getenv("DB_PATH", "db.sqlite"))

    from openwrite.utils.db import SessionLocal
    session = SessionLocal

    capsule.add("/",
        blog_index,
        protocol='gemini')

    capsule.add("/p/*",
        blog_post,
        protocol='gemini')


