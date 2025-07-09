from flask import Blueprint, render_template, redirect, request, session, g
from openwrite.utils.models import User
import bcrypt
import re
import requests
import json

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if g.user is not None:
        return redirect("/dashboard")

    if not g.register_enabled:
        return redirect("/")

    if request.method == "GET":
        return render_template('register.html')

    form_username = request.form.get('username')
    if not re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9_-]{1,28}[a-zA-Z0-9])?$", form_username):
        return render_template('register.html', error=g.trans['wrong_username'])
    form_password = request.form.get('password')
    form_password2 = request.form.get('password2')

    if form_password != form_password2:
        return render_template("register.html", error=g.trans['password_dont_match'])

    user = g.db.query(User).filter_by(username=form_username).first()
    if user:
        return render_template('register.html', error=g.trans["user_exists"])
    
    if g.captcha:
        if request.form.get("frc-captcha-response") is None or request.form.get("frc-captcha-response") == ".ACTIVATED":
            return render_template('register.html', error=g.trans['invalid_captcha'])

        captcha_data = {'response': request.form.get("frc-captcha-response"), 'sitekey': g.fcaptcha_sitekey}

        resp = requests.post("https://global.frcapi.com/api/v2/captcha/siteverify", json=captcha_data, headers={"X-API-Key": g.fcaptcha_apikey})

        if json.loads(resp.text)['success'] != True:
            return render_template("register.html", error=resp.text)
    
    try: 
        hashed = bcrypt.hashpw(form_password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=form_username, email="", password_hash=hashed.decode('utf-8'), verified=0, admin=0)
        g.db.add(new_user)
        g.db.commit()
        return render_template("register.html", message=g.trans["registered"])
    except Exception:
        g.db.rollback()
        return render_template('register.html', error=g.trans["error"])

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect("/dashboard")

    if request.method == "GET":
        return render_template('login.html')

    form_username = request.form.get('username')
    form_password = request.form.get('password')

    user = g.db.query(User).filter_by(username=form_username).first()
    if user and bcrypt.checkpw(form_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        session["userid"] = user.id
        session["admin"] = user.admin
        return redirect("/dashboard")
    else:
        return render_template('login.html', error=g.trans["invalid_credentials"])

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

