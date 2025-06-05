from flask import Flask, render_template, request, g, redirect, make_response, session
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import json
from db import SessionLocal
from models import User
import bcrypt

load_dotenv()

pwd = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__, template_folder='%s/templates' % pwd)
app.secret_key = os.getenv("SECRET_KEY")

with open("i18n.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

def get_current_lang():
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

    return lang

@app.before_request
def init_data():
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

    if session.get("userid") is not None:
        g.user = session.get("userid")
    else:
        g.user = None

@app.context_processor
def inject_globals():
    return {
        'current_lang': get_current_lang(),
        'available_languages': {
            'en': {'name': 'English', 'flag': '🇬🇧'''},
            'pl': {'name': 'Polski', 'flag': '🇵🇱'}
        }
    }

@app.route("/set-lang/<lang_code>")
def set_lang(lang_code):
    if lang_code not in translations:
        return redirect("/")

    resp = make_response(redirect(request.referrer or "/"))
    resp.set_cookie("lang", lang_code, max_age=60*60*24*365)
    return resp

@app.route("/")
def index():
    if g.user is not None:
        return redirect("/dashboard")
    
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if g.user is not None:
        return redirect("/dashboard")
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        form_username = request.form.get('username')
        form_password = request.form.get('password')
        form_email = request.form.get('email')
        user = g.db.query(User).filter_by(username=form_username).first()
        if user:
            return render_template('register.html', error=g.trans["user_exists"])
        
        try: 
            hashed = bcrypt.hashpw(form_password.encode('utf-8'), bcrypt.gensalt())
            new_user = User(username=form_username, email=form_email, password_hash=hashed.decode('utf-8'))
            g.db.add(new_user)
            g.db.commit()
            return render_template("register.html", message=g.trans["registered"])
        except SQLAlchemError as e:
            g.db.rollback()
            return render_template('register.html', error=g.trans["error"])


@app.route("/login", methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect("/dashboard")
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        form_username = request.form.get('username')
        form_password = request.form.get('password')
        user = g.db.query(User).filter_by(username=form_username).first()
        if user and bcrypt.checkpw(form_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            session["userid"] = user.id
            return redirect("/dashboard")
        else:
            return render_template('login.html', error=g.trans["invalid_credentials"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if g.user is None:
        return redirect("/login")

    return render_template("dashboard.html")

if __name__ == "__main__":
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.run(host=os.environ.get("IP"), port=os.environ.get("PORT"))
