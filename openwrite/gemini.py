import os, subprocess
from dotenv import load_dotenv

from jetforce import (
    JetforceApplication, Request, Response, Status
)
from openwrite.utils.db import init_engine, SessionLocal
from openwrite.utils.models import Blog, Post, User, View
from md2gemini import md2gemini
from datetime import datetime, timezone

session = None

class OpenwriteGemini(JetforceApplication):

    def __init__(self):
        super().__init__()
        global session
        load_dotenv()
        init_engine(os.getenv("DB_TYPE", "sqlite"),
                    os.getenv("DB_PATH", "db.sqlite"))

        from openwrite.utils.db import SessionLocal
        session = SessionLocal

        self.route(r"/b/(?P<blogname>[^/]+)/(?P<slug>[^/]+)$")(self.post_view)
        self.route(r"/b/(?P<blogname>[^/]+)/?$")(self.blog_index)
        self.route("")(self.root)

    def blog_index(self, request: Request, blogname: str) -> Response:
        global session
        try:
            blog = session.query(Blog).filter_by(name=blogname).first()
            if not blog:
                return Response(Status.NOT_FOUND, "Blog not found")

            posts = (session.query(Post)
                            .filter_by(blog=blog.id)
                            .order_by(Post.id.desc())
                            .all())

            body = f"# {blogname}\n\n"
            body += md2gemini(blog.description_raw)
            body += "\n\n"
            for post in posts:
                body += f"=> /b/{blogname}/{post.link} {post.title}\n"
            return Response(Status.SUCCESS, "text/gemini", body)

        finally:
            session.close()

    def post_view(self, request: Request, blogname: str, slug: str) -> Response:
        global session
        try:
            blog = session.query(Blog).filter_by(name=blogname).first()
            if not blog:
                return Response(Status.NOT_FOUND, "Blog not found")

            post = (session.query(Post)
                          .filter_by(blog=blog.id, link=slug)
                          .first())
            if not post:
                return Response(Status.NOT_FOUND, "Post not found")
    
            user = session.query(User).filter_by(id=blog.owner).first()

            now = datetime.now(timezone.utc)
            new_view = View(blog=blog.id, post=post.id, hash="127.0.0.1", date=now, agent="gemini")
            session.add(new_view)
            session.commit()

            post.authorname = user.username
            gemtext = f"=> /b/{blog.name} {blog.title}\n"
            gemtext += f"# {post.title}\n\n"
            gemtext += f"{post.date} "
            if post.author != "0":
                gemtext += f"by {post.authorname}"
            gemtext += f"\n\n{md2gemini(post.content_raw)}"
            return Response(Status.SUCCESS, "text/gemini", gemtext)

        finally:
            session.close()

    def root(self, request: Request) -> Response:
        global session
        resp = "# openwrite - now on gemini too\n\n##Latest posts:\n"
        try:
            posts = (session.query(Post).filter_by(feed="1").order_by(Post.id.desc()).limit(10).all())
            for p in posts:
                blog = session.query(Blog).filter_by(id=p.blog).first()
                resp += f"\n{p.date} - {blog.title}\n"
                resp += f"=> /b/{blog.name}/{p.link} {p.title}\n"
            return Response(
                Status.SUCCESS,
                "text/gemini",
                resp
            )

        finally:
            session.close()

def create_gemini():
    from jetforce.server import GeminiServer
    gemini_certs = os.getenv("GEMINI_CERTS")
    main_domain = os.getenv("DOMAIN")
    GeminiServer(
        OpenwriteGemini(),
        host="0.0.0.0",
        port=int(os.getenv("GEMINI_PORT", 1965)),
        
        certfile=f"{gemini_certs}/cert.pem", 
        keyfile=f"{gemini_certs}/key.pem",
        hostname=main_domain
    ).run()

