from flask import Flask, g
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from openwrite.utils.models import Info
import os
from .utils.helpers import generate_nonce
import time

start_time = time.time()


def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", subdomain_matching=True, static_url_path='/static')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=1, x_host=1, x_port=1)
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
    db_type = os.getenv("DB_TYPE", "sqlite")
    db_path = os.getenv("DB_PATH", "db.sqlite")

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

        g.trans = translations[lang]
        g.alltrans = translations
        g.lang = lang
        g.db = SessionLocal()
        g.main_domain = os.getenv("DOMAIN")
        g.blog_limit = os.getenv("BLOG_LIMIT")
        g.upload_enabled = os.getenv("MEDIA_UPLOAD", "no") == "yes"
        g.captcha = os.getenv("CAPTCHA_ENABLED", "no") == "yes"
        g.fcaptcha_sitekey = os.getenv("FRIENDLY_CAPTCHA_SITEKEY", "key")
        g.fcaptcha_apikey = os.getenv("FRIENDLY_CAPTCHA_APIKEY", "api_key")

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
    def set_headers(response):
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

    @app.route("/debug")
    def debug():
        from flask import request
        return {
            "remote_addr": request.remote_addr,
            "access_route": request.access_route,
            "headers": dict(request.headers)
        }

    return app
