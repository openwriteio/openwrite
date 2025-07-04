from flask import Flask, g
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
import os
from .utils.helpers import generate_nonce, get_ip
import time
from .utils.models import Settings

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
    from .utils.translations import load_translations
    from .utils.db import init_engine, SessionLocal
    from flask_cors import CORS
    
    translations = load_translations()
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

    @app.before_request
    def before():
        from flask import request, session
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

        g.mode = os.getenv("MODE")
        f_abs_path = os.path.abspath(__file__)
        g.mainpath = "/".join(f_abs_path.split("/")[:-1])
        g.trans = translations[lang]
        g.alltrans = translations
        g.lang = lang
        g.db = SessionLocal
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
        return {
            'current_lang': g.lang,
            'available_languages': {
                'en': {'name': 'English', 'flag': '🇬🇧'},
                'pl': {'name': 'Polski', 'flag': '🇵🇱'}
            }
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
