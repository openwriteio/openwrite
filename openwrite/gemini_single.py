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
                if not blog:
                    return "not found"
                posts = (session.query(Post)
                        .filter_by(blog=blog.id)
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

def blog_post(req):
    global session
    path = req.path
    if len(path.split("/")) == 3:
        
        slug = path.split("/")[2]
        try:
            blog = session.query(Blog).filter_by(name="default").first()
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
        blog_index,
        protocol='gemini')

    capsule.add("/p/*",
        blog_post,
        protocol='gemini')
