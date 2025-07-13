from flask import Flask, g
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
import os
from .utils.helpers import generate_nonce, get_ip
import time
from .utils.models import Settings, Home
from sqlalchemy import distinct
import bcrypt
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timezone

start_time = time.time()

def create_app(test_config=None):
    if test_config is None:
        load_dotenv()
        db_type = os.getenv("DB_TYPE", "sqlite")
        db_path = os.getenv("DB_PATH", "db.sqlite")
    else:
        db_type = test_config.get("DB_TYPE", "sqlite")
        db_path = test_config.get("DB_PATH", "data.db")
        load_dotenv(test_config.get("env"), override=True)

    if not os.path.exists(".initialized") or test_config is not None:
        mode = os.getenv("MODE")
        domain = os.getenv("DOMAIN")
        f_abs_path = os.path.abspath(__file__)
        file_cwd = "/".join(f_abs_path.split("/")[:-1])
        from .utils.create_db import init_db
        init_db(db_type, db_path)
        from .utils.models import User, Blog, Post, Settings, Home
        from .utils.db import init_engine, SessionLocal
        init_engine(db_type, db_path)
        from .utils.db import SessionLocal
        admin_password = os.urandom(16).hex()
        hashed = bcrypt.hashpw("openwrite".encode("utf-8"), bcrypt.gensalt())
        admin_user = User(username="admin", email="", password_hash=hashed.decode("utf-8"), verified=1, admin=1)
        SessionLocal.add(admin_user)
        SessionLocal.commit()
        SessionLocal.close()
        
        if mode == "single":
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

            new_blog = Blog(
                owner=1, 
                name="default", 
                title=domain, 
                index="on", 
                access="domain",
                description_raw=f"![hello](https://openwrite.b-cdn.net/hello.jpg =500x258)\n\n# Hello there! 👋\n\nYou can edit your blog description in [dashboard](http://{domain}/dashboard/edit/default)",
                description_html=f"<p><img src=\"https://openwrite.b-cdn.net/hello.jpg\" width=\"500\" height=\"258\"></p><h1>Hello there! 👋</h1><p>You can edit your blog description in <a href=\"http://{domain}/dashboard/edit/default\">dashboard</a></p>",
                css="",
                pub_key=public_pem,
                priv_key=private_pem,
                theme="default",
                created=now
            )
            SessionLocal.add(new_blog)

        hometext_pl = """
                 <h1 class="centered"><span style="color: #f2d2c8">cicha</span> przestrzeń na <span style="color: #5a36bf">głośne</span> myśli.</h1>
                
                <article class="main-content" style="text-align: center">
                    <p><strong>Openwrite</strong> to lekka, otwartoźródłowa platforma blogowa stworzona z myślą o wolności pisania – bez reklam, trackerów i zbędnego balastu.</p><br>

          - Pisz w Markdownie<br>
          - Zainstaluj w kilka minut<br>
          - Publikuj do sieci, przez Gemini lub na Mastodonie – jak chcesz<br>

        <br>
        <p>Bez analityki. Bez ukrytych skryptów.<br>
        Tylko Ty, Twoje myśli i miejsce, w którym możesz je wyrazić.</p>
        <p>Wybierz motyw. Dodaj obrazki. Śledź wyświetlenia.<br>
        Zbuduj bloga po swojemu – minimalistycznego lub z dodatkami.</p>
        <p><strong>To Twoje słowa. Twój blog. Twoje zasady.</strong><br><br>
        Zacznij pisać — i odzyskaj głos.</p>
                    </p>
                </article>
                <div class="action-links">
                    <a class="btn purple" href="/register">Zarejestruj się tutaj</a>
                    <span class="or-separator">lub</span>
                    <a class="btn empty" href="https://main.openwrite.io/hosting">Samodzielny hosting</a>
                </div>
        """

        hometext_en = """
                 <h1 class="centered"><span style="color: #f2d2c8">quiet</span> space for <span style="color: #5a36bf">loud</span> thoughts.</h1>
                
                <article class="main-content" style="text-align: center">
                    <p><strong>Openwrite</strong> is a lightweight, open-source blogging platform built for people who just want to write — without ads, trackers, or bloated nonsense.</p><br>

          - Write in Markdown<br>
          - Self-host in minutes<br>
          - Publish to the open web, Gemini, or Mastodon — your choice<br>

        <br>
        <p>There’s no analytics. No hidden scripts. No engagement traps.<br>
        Just you, your thoughts, and an honest place to share them.</p>
        <p>Choose a theme. Add images. Track views.<br>
        Build your blog your way — minimal or feature-rich.</p>
        <p><strong>It’s your voice. Your blog. Your rules.</strong><br><br>
        Start writing — and own your words.</p>
                </article>
                <div class="action-links">
                    <a class="btn purple" href="/register">Register Here</a>
                    <span class="or-separator">or</span>
                    <a class="btn empty" href="https://main.openwrite.io/hosting">Self Host</a>
                </div>
        """

        with open(f"{file_cwd}/utils/i18n.json", "r", encoding='utf-8') as f:
            data = json.load(f)
            
        for lang, entries in data.items():
            for key, value in entries.items():
                SessionLocal.add(Home(language=lang, name=key, type="translation", content=value))

        new_setting = Settings(name="logo", value="/static/logo.png")
        new_home_pl = Home(language="pl", name="hometext", type="text", content=hometext_pl)
        new_home_en = Home(language="en", name="hometext", type="text", content=hometext_en)
        SessionLocal.add(new_setting)
        SessionLocal.add(new_home_pl)
        SessionLocal.add(new_home_en)
        SessionLocal.commit()

        if test_config is None:
            with open(".initialized", "w") as f:
                f.write("ok")

    app = Flask(__name__, template_folder="templates", subdomain_matching=True, static_url_path='/static')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['SERVER_NAME'] = os.getenv("DOMAIN")

    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.blog import blog_bp
    from .routes.admin import admin_bp
    from .routes.main import main_bp
    from .routes.upload import upload_bp
    from .routes.federation import federation_bp
    from .utils.db import init_engine, SessionLocal
    from flask_cors import CORS
    
    CORS(app)

    init_engine(db_type, db_path)    
    from .utils.db import SessionLocal

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(federation_bp)

    def _(key: str):
        return g.trans.get(key, key)

    app.jinja_env.globals['_'] = _

    @app.before_request
    def before():
        from flask import request, session
        from openwrite.utils.models import Home, Settings
        g.db = SessionLocal
        t_query = g.db.query(distinct(Home.language)).all()
        translations = [row[0] for row in t_query]
        lang = request.cookies.get("lang")
        if not lang or lang not in translations:
            accept = request.headers.get("Accept-Language", "")
            for part in accept.split(","):
                code = part.split("-")[0].strip().lower()
                if code in translations:
                    lang = code
                    break
        if lang not in translations:
            lang = "en"

        trans = g.db.query(Home).filter(Home.type == "translation", Home.language == lang).all()
        
        g.mode = os.getenv("MODE")
        f_abs_path = os.path.abspath(__file__)
        g.mainpath = "/".join(f_abs_path.split("/")[:-1])
        g.trans = {t.name: t.content for t in trans if len(t.content) > 1}
        g.alltrans = translations
        g.lang = lang
        g.main_domain = os.getenv("DOMAIN")
        g.blog_limit = os.getenv("BLOG_LIMIT")
        g.register_enabled = os.getenv("SELF_REGISTER", "no") == "yes"
        g.upload_enabled = os.getenv("MEDIA_UPLOAD", "no") == "yes"
        g.captcha = os.getenv("CAPTCHA_ENABLED", "no") == "yes"
        g.fcaptcha_sitekey = os.getenv("FRIENDLY_CAPTCHA_SITEKEY", "key")
        g.fcaptcha_apikey = os.getenv("FRIENDLY_CAPTCHA_APIKEY", "api_key")
        g.staticdir = app.static_folder
        g.staticurl = app.static_url_path
        g.settings = g.db.query(Settings).all()

        if session.get("userid") is not None:
            g.user = session.get("userid")
            g.isadmin = session.get("admin")
        else:
            g.user = None

        g.nonce = generate_nonce()

    @app.context_processor
    def inject_globals():
        from openwrite.utils.models import Home
        langs = g.db.query(Home).filter_by(name="lang_name").all()
        lang_obj = {}
        for l in langs:
            lang_obj[l.language] = {"name": l.content}
        return {
            'current_lang': g.lang,
            'available_languages': lang_obj
        }

    @app.after_request
    def after(response):
        nonce = g.nonce
        #response.headers["Content-Security-Policy"] = (
        #    f"default-src 'none'; "
        #    f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net http://{g.main_domain}"
        #    f"style-src 'self'; "
        #    f"style-src-elem 'self' http://{g.main_domain}; "
        #    f"style-src-attr 'unsafe-inline';"
        #    f"script-src-attr 'unsafe-inline';"
        #    f"img-src 'self' data: http://{g.main_domain}; "
        #    f"font-src 'self'; "
        #    f"connect-src 'self'; "
        #    f"base-uri 'none'; "
        #    f"form-action 'self'; "
        #    f"frame-ancestors 'none';"
        #    f"frame-src https://global.frcapi.com ;"
        #)
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e

        app.logger.exception(f"Unhandled exception! {e}")
        return "Internal Server Error", 500

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        g.db.remove()

    return app
