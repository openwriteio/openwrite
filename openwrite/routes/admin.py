from flask import Blueprint, render_template, redirect, g, request, make_response
import json
from openwrite.utils.models import Blog, User, Settings, Home, Post
import re
import bcrypt
from werkzeug.utils import secure_filename
from PIL import Image
import os
from collections import defaultdict

admin_bp = Blueprint("admin", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

@admin_bp.route("/admin")
def admin():
    """
    Admin dashboard to manage blogs and users.
    """
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
    """
    Delete a blog by its name.
    """
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    b = g.db.query(Blog).filter_by(name=blog).first()
    if b:
        g.db.delete(b)
        g.db.commit()

    return redirect("/admin")

@admin_bp.route("/admin/delete_user/<username>")
def admin_delete_user(username):
    """
    Delete a user and all their blogs.
    """
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
    """
    Grant admin privileges to a user.
    """
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
    """
    Remove admin privileges from a user.
    """
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
    """
    Add a new user to the system.
    """
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")
    if request.method == "GET":
        return render_template("register.html", add="1", captcha="0")
    
    form_username = request.form.get('username')
    if not re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9_-]{1,28}[a-zA-Z0-9])?$", form_username):
        return render_template('register.html', error='wrong_username', add="1", captcha="0")
    form_password = request.form.get('password')
    form_password2 = request.form.get('password2')

    if form_password != form_password2:
        return render_template("register.html", error='password_dont_match', add="1", captcha="0")

    user = g.db.query(User).filter_by(username=form_username).first()
    if user:
        return render_template('register.html', error="user_exists", add="1", captcha="0")

    try: 
        hashed = bcrypt.hashpw(form_password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=form_username, email="", password_hash=hashed.decode('utf-8'), verified=0, admin=0)
        g.db.add(new_user)
        g.db.commit()
        return redirect("/admin")
    except Exception as e:
        print(e)
        g.db.rollback()
        return render_template('register.html', error='error', add="1", captcha="0")


@admin_bp.route("/admin/settings", methods=['GET', 'POST'])
def admin_settings():
    """
    Manage application settings.
    """
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
            return render_template("settings.html", settings=settings_dict, hometext=hometext, error='invalid_filename')

        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            return render_template("settings.html", settings=settings_dict, hometext=hometext, error='unsupported_filetype')

        try:
            img = Image.open(file.stream)
            img.verify()
        except Exception:
            return render_template("settings.html", settings=settings_dict, hometext=hometext, error="not_image")

        file.stream.seek(0)

        filepath = os.path.join(g.staticdir, filename)
        file.save(filepath)
        logo_file = filepath
        logo_q = g.db.query(Settings).filter_by(name="logo").first()
        logo_q.value = f"{g.staticurl}/{filename}"
        g.db.commit()
        settings_dict['logo'] = f"{g.staticurl}/{filename}"
    g.db.query(Home).filter_by(name="hometext").delete()
    for h in hometexts.keys():
        g.db.add(Home(name="hometext", language=h, type="text", content=hometexts[h]))
    g.db.commit()
    new_hometexts = g.db.query(Home).filter_by(name="hometext").all()
    return render_template("settings.html", settings=settings_dict, hometext=new_hometexts)

@admin_bp.route("/admin/translations", methods=['GET', 'POST'])
def translations():
    """
    Manage translations for the application.
    Allows viewing, editing, and saving translations.
    (I can't believe I didn't secured it earlier lol)
    """
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    if request.method == "GET":
        trans = g.db.query(Home).filter_by(type="translation").all()
        grouped = defaultdict(dict)
        for t in trans:
            grouped[t.name][t.language] = t.content
        return render_template("translations.html", trans=grouped, langs=g.alltrans)

    trans_array = []
    for key, val in request.form.items():
        if key.startswith("val_"):
            _, name, lang = key.split("___", 2)
            trans_array.append({
                "name": name,
                "language": lang,
                "content": val
            })

    g.db.query(Home).filter(Home.type == "translation").delete()

    for tr in trans_array:
        g.db.add(Home(name=tr['name'], language=tr['language'], content=tr['content'], type="translation"))

    g.db.commit()
    return redirect("/admin/translations")

@admin_bp.route("/admin/download_translations")
def download_translations():
    """
    Download all translations as a json file.
    """
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    translations = g.db.query(Home).filter_by(type="translation").all()
    trans_dict = defaultdict(dict)
    for t in translations:
        trans_dict[t.language][t.name] = t.content
    
    response = make_response(json.dumps(dict(trans_dict), ensure_ascii=False))
    response.headers["Content-Disposition"] = "attachment; filename=i18n.json"
    response.headers["Content-Type"] = "application/json"
    return response

@admin_bp.route("/admin/remove_from_feed/<int:post_id>")
def remove_from_feed(post_id):
    """
    Remove a post from the discover feed.
    """
    if g.user is None or g.isadmin == 0 or g.mode == "single":
        return redirect("/")

    post = g.db.query(Post).filter_by(id=post_id).first()
    if post:
        post.feed = "0"
        g.db.commit()

    return redirect("/discover")