import os, subprocess
from dotenv import load_dotenv
from openwrite.utils.db import init_engine, SessionLocal
from openwrite.utils.models import Blog, Post, User, View, Page
from openwrite.utils.helpers import anonymize
from md2gemini import md2gemini
from datetime import datetime, timezone
import re
session = None

openwrite_logo = """
                                                    
                                     .-.    /       
  .-._..-.   .-..  .-. `)    (  ).--.`-'---/---.-.  
 (   ) /  )./.-'_)/   )/  .   )/    /     /  ./.-'_ 
  `-' /`-' (__.''/   ((_.' `-'/  _.(__.  /   (__.'  
     /                `-                            
                            quiet space for loud thoughts
"""

def root(req):
    global session
    resp = f"```\n{openwrite_logo}\n```"
    resp += "\nopenwrite.io is a minimalist blogging platform built for writing freely, hosting independently, and publishing without noise. To create your own blog, visit:\n"
    resp += "=> https://openwrite.io openwrite.io\n"
    resp += "In here you can read posts published.\n"
    resp += "\n## 🗞️ Latest posts:\n"
    try:
        posts = (session.query(Post).filter(Post.feed == "1", Post.isdraft == "0").order_by(Post.id.desc()).limit(10).all())
        for p in posts:
            blog = session.query(Blog).filter_by(id=p.blog).first()
            resp += f"\n{p.date} - 📓 {blog.title}\n"
            resp += f"=> /b/{blog.name}/{p.link} {p.title}\n"
        return resp

    finally:
        session.close()

def blog_index(req):                                                                           
        global session
        path = req.path
        if len(path.split("/")) == 3:
            blogname = path.split("/")[2]
            try:
                blog = session.query(Blog).filter_by(name=blogname).first()
                if not blog:
                    return "not found"
                posts = (session.query(Post)
                        .filter_by(blog=blog.id, isdraft="0")
                        .order_by(Post.id.desc())
                        .all())
                pages = (session.query(Page)
                        .filter(Page.blog == blog.id, Page.show == "1").all())
                homepage = session.query(Page).filter(Page.blog == blog.id, Page.url == "").first()
                body = f"# 📓 {blog.title}\n\n"
                posts_data = ""
                for post in posts:
                    posts_data += f"=> /b/{blogname}/{post.link} {post.title}\n\n"
                pages_data = ""
                for page in pages:
                    pages_data += f"=> /b/{blogname}/{page.url} {page.name}\n\n"
                content = pages_data + "\n"
                content += homepage.content_raw.replace('{posts}', f"\n{posts_data}")
                content = re.sub(r'!\[(.*?)\]\((.*?)\s*=\d+x\d+\)', r'![\1](\2)', content)
                body += md2gemini(content)
                
                return body
            finally:
                session.close()
        elif len(path.split("/")) == 4:
            
            blogname = path.split("/")[2]
            slug = path.split("/")[3]
            try:
                blog = session.query(Blog).filter_by(name=blogname).first()
                if not blog:
                    return "not found"

                post = (session.query(Post)
                              .filter_by(blog=blog.id, link=slug, isdraft="0")
                              .first())
                if not post:
                    page = (session.query(Page)
                              .filter_by(blog=blog.id, url=slug)
                              .first())
                    if page:
                        content = f"=> /b/{blog.name} 📓 {blog.title}\n\n"
                        content += page.content_raw
                        content = re.sub(r'!\[(.*?)\]\((.*?)\s*=\d+x\d+\)', r'![\1](\2)', content)
                        return md2gemini(content)
                    else:
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
                content = post.content_raw
                content = re.sub(r'!\[(.*?)\]\((.*?)\s*=\d+x\d+\)', r'![\1](\2)', content)
                gemtext += f"\n\n{md2gemini(content)}\n\n"
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
        root,
        protocol='gemini')

    capsule.add("/b/*",
        blog_index,
        protocol='gemini')
