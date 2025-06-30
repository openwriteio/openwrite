from flask import Blueprint, render_template, redirect, g, request
from openwrite.utils.models import Blog, User, Settings, Home
import re
import bcrypt
from werkzeug.utils import secure_filename
from PIL import Image
import os

admin_bp = Blueprint("admin", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

@admin_bp.route("/admin")
def admin():
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    blogs = g.db.query(Blog).all()
    for b in blogs:
        u = g.db.query(User).filter_by(id=b.owner).first()
        b.ownername = u.username
    users = g.db.query(User).all()

    return render_template("admin.html", blogs=blogs, users=users)

@admin_bp.route("/admin/delete_blog/<blog>")
def admin_delete_blog(blog):
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    b = g.db.query(Blog).filter_by(name=blog).first()
    if b:
        g.db.delete(b)
        g.db.commit()

    return redirect("/admin")

@admin_bp.route("/admin/delete_user/<username>")
def admin_delete_user(username):
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    if username == "admin":
        return redirect("/admin")

    user = g.db.query(User).filter_by(username=username).first()
    if not user:
        return redirect("/admin")

    user_blogs = g.db.query(Blog).filter_by(owner=user.id).all()
    for b in user_blogs:
        g.db.delete(b)

    g.db.delete(user)
    g.db.commit()

    return redirect("/admin")

@admin_bp.route("/admin/make_admin/<username>")
def admin_make_admin(username):
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    user = g.db.query(User).filter_by(username=username).first()
    if not user:
        return redirect("/admin")

    user.admin = "1"
    g.db.commit()

    return redirect("/admin")

@admin_bp.route("/admin/remove_admin/<username>")
def admin_remove_admin(username):
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    if username == "admin":
        return redirect("/admin")

    user = g.db.query(User).filter_by(username=username).first()
    if not user:
        return redirect("/admin")

    user.admin = "0"
    g.db.commit()

    return redirect("/admin")

@admin_bp.route("/admin/add_user", methods=['GET', 'POST'])
def admin_add_user():
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")
    if request.method == "GET":
        return render_template("register.html", add="1", captcha="0")
    
    form_username = request.form.get('username')
    if not re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9_-]{1,28}[a-zA-Z0-9])?$", form_username):
        return render_template('register.html', error=g.trans['wrong_username'], add="1", captcha="0")
    form_password = request.form.get('password')
    form_password2 = request.form.get('password2')

    if form_password != form_password2:
        return render_template("register.html", error=g.trans['password_dont_match'], add="1", captcha="0")

    user = g.db.query(User).filter_by(username=form_username).first()
    if user:
        return render_template('register.html', error=g.trans["user_exists"], add="1", captcha="0")

    try: 
        hashed = bcrypt.hashpw(form_password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=form_username, email="", password_hash=hashed.decode('utf-8'), verified=0, admin=0)
        g.db.add(new_user)
        g.db.commit()
        return redirect("/admin")
    except Exception as e:
        print(e)
        g.db.rollback()
        return render_template('register.html', error=g.trans["error"], add="1", captcha="0")


@admin_bp.route("/admin/settings", methods=['GET', 'POST'])
def admin_settings():
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    settings = g.db.query(Settings).all()
    hometext = g.db.query(Home).filter_by(name="hometext").all()
    settings_dict = {s.name: s.value for s in settings}

    if request.method == "GET":
        return render_template("settings.html", settings=settings_dict, hometext=hometext)

    hometexts = {}
    pattern = re.compile(r'^hometext_(\w+)$')
    for key, value in request.form.items():
        match = pattern.match(key)
        if match:
            lang = match.group(1)
            hometexts[lang] = value

    if "logo" in request.files and request.files['logo'].filename != "":
        file = request.files['logo']
        filename = secure_filename(file.filename)
        if "." not in filename:
            return render_template("settings.html", settings=settings_dict, hometext=hometext, error="Wrong file!")

        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            return render_template("settings.html", settings=settings_dict, hometext=hometext, error="Wrong extension!")

        try:
            img = Image.open(file.stream)
            img.verify()
        except Exception:
            return render_template("settings.html", settings=settings_dict, hometext=hometext, error="File is not image!")

        file.stream.seek(0)

        filepath = os.path.join(g.staticdir, filename)
        file.save(filepath)
        logo_file = filepath
        logo_q = g.db.query(Settings).filter_by(name="logo").first()
        logo_q.value = f"{g.staticurl}/{filename}"
        g.db.commit()
        settings_dict['logo'] = f"{g.staticurl}/{filename}"
    for h in hometext:
        h.content = hometexts[h.language]
    g.db.commit()
    return render_template("settings.html", settings=settings_dict, hometext=hometext)
