from flask import Flask
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
import os



def create_app():
    load_dotenv()
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

    @app.before_request
    def before():
        from flask import g, request, session
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
        g.lang = lang
        g.db = SessionLocal()
        g.main_domain = os.getenv("DOMAIN")
        g.blog_limit = os.getenv("BLOG_LIMIT")
        g.upload_enabled = os.getenv("MEDIA_UPLOAD", "no") == "yes"

        if session.get("userid") is not None:
            g.user = session.get("userid")
            g.isadmin = session.get("admin")
        else:
            g.user = None

    @app.context_processor
    def inject_globals():
        return {
            'current_lang': translations.get('current_lang', 'en'),
            'available_languages': {
                'en': {'name': 'English', 'flag': '🇬🇧'},
                'pl': {'name': 'Polski', 'flag': '🇵🇱'}
            }
        }

    return app
