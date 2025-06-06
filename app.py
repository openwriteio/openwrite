from flask import Flask, render_template, request, g, redirect, make_response, session, jsonify
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import json
from db import SessionLocal
from models import User, Blog, Post
import bcrypt
import time
import bleach
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import requests
from PIL import Image
import hashlib
import re
import unicodedata

start_time = time.time()

load_dotenv()

pwd = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__, template_folder='%s/templates' % pwd, subdomain_matching=True)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SERVER_NAME'] = os.getenv("DOMAIN")
UPLOAD_ENABLED = os.getenv("MEDIA_UPLOAD", "no") == "yes"
STORAGE_BACKEND = os.getenv("UPLOAD_STORAGE", "local")
BUNNY_API_KEY = os.getenv("BUNNY_API_KEY")
BUNNY_ZONE = os.getenv("BUNNY_STORAGE_ZONE")
BUNNY_URL = os.getenv("BUNNY_STORAGE_URL")
version = "0.1"

with open("i18n.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

def sanitize_html(content):
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'hr',
        'strong', 'b', 'em', 'i', 'u',
        'ul', 'ol', 'li',
        'a', 'img',
        'code', 'pre', 'del',
        'blockquote',
        'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td'
    ]

    allowed_attrs = {
        'a': ['href', 'title', 'rel', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'th': ['align'],
        'td': ['align'],
    }

    cleaned_html = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)
    return cleaned_html


def gen_link(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '-', text.strip())

    return text


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
    g.main_domain = os.getenv("DOMAIN")
    g.blog_limit = os.getenv("BLOG_LIMIT")
    g.upload_enabled = UPLOAD_ENABLED

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

# DO NOT remove this code!
@app.route('/.well-known/openwrite')
def show_instance():
    blog_count = g.db.query(Blog).count()
    user_count = g.db.query(User).count()
    return {"openwrite version": version, "blogs_running": blog_count, "users": user_count, "uptime": (time.time() - start_time) }


@app.route("/upload_image", methods=["POST"])
def upload_image():
    if not UPLOAD_ENABLED:
        return jsonify({"error": "Uploads disabled"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    if g.user is None:
        return jsonify({"error": "unauthorized"}), 403

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    user = g.db.query(User).filter_by(id=g.user).first()

    file = request.files['file']
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.')[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Unsupported file type. Image only."}), 400

    try:
        img = Image.open(file.stream)
        img.verify()
    except Exception:
        return jsonify({"error": "Uploaded image is not a valid image."}), 400

    file.stream.seek(0)

    m = hashlib.md5()
    m.update(filename.encode() + user.username.encode())

    filename = user.username + "_" + m.hexdigest() + "." + extension

    if STORAGE_BACKEND == "bunny":
        url = f"https://storage.bunnycdn.com/{BUNNY_ZONE}/{filename}"
        print(url)
        headers = {
            "AccessKey": BUNNY_API_KEY,
            "Content-Type": "application/octet-stream",
            "accept": "application/json"
        }
        response = requests.put(url, headers=headers, data=file)
        if response.ok:
            return jsonify({"url": f"{BUNNY_URL}{filename}"})
        else:
            return jsonify({"error": "Bunny upload failed", "detail": response.text}), 500

    elif STORAGE_BACKEND == "local":
        os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(LOCAL_UPLOAD_DIR, filename)
        file.save(filepath)
        return jsonify({"url": f"/{LOCAL_UPLOAD_DIR}/{filename}"})

    else:
        return jsonify({"error": "Invalid storage backend"}), 500

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
        except SQLAlchemyError as e:
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

    user_blogs = g.db.query(Blog).filter_by(owner=g.user).all()

    return render_template("dashboard.html", blogs=user_blogs)

@app.route("/dashboard/create", methods=['GET', 'POST'])
def create_blog():
    if g.user is None:
        return redirect("/login")
    count = g.db.query(Blog).filter_by(owner=g.user).count()
    if count >= int(g.blog_limit):
        return redirect("/dashboard")
    if request.method == "GET":
        return render_template("create.html")
    elif request.method == "POST":
        form_name = request.form.get("name")
        blog = g.db.query(Blog).filter_by(name=form_name).first()
        if blog:
            return render_template("create.html", error="This name already exists!")
        
        form_index = request.form.get("index")
        if form_index is None:
            form_index = "off"
        form_access = request.form.get("access")
        try:
            new_blog = Blog(owner=g.user, title=form_name, name=form_name, index=form_index, access=form_access, description_raw="# my new awesome blog on " + os.getenv("DOMAIN") + "\n![alt text](https://naszkawalekswiata.pl/wp-content/uploads/2021/07/seljalandsfoss-7-473x630.jpg)", description_html="<h1>my new awesome blog on " + os.getenv("DOMAIN") + "</h1><img src=\"https://naszkawalekswiata.pl/wp-content/uploads/2021/07/seljalandsfoss-7-473x630.jpg\" width=\"500\" height=\"auto\" alt=\"alt text\">")
            g.db.add(new_blog)
            g.db.commit()
            return redirect("/dashboard")
        except Exception as e:
            return render_template("create.html", error=g.trans['error'])

@app.route("/dashboard/delete/<name>")
def delete_blog(name):
    if g.user is None:
        return redirect("/login")
    
    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None:
        return redirect("/dashboard")

    if blog.owner != g.user:
        return redirect("/dashboard")

    g.db.delete(blog)
    g.db.commit()
    return redirect("/dashboard")

@app.route("/dashboard/edit/<name>", methods=['GET', 'POST'])
def edit_blog(name):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None:
        return redirect("/dashboard")

    if blog.owner != g.user:
        return redirect("/dashboard")

    posts = g.db.query(Post).filter_by(blog=blog.id).all()
    if request.method == "GET":
       return render_template("edit.html", blog=blog, posts=posts)

    elif request.method == "POST":
        description_raw = request.form.get("description_raw")
        description_html = sanitize_html(request.form.get("description_html"))
        blog.description_raw = description_raw
        blog.description_html = description_html
        g.db.commit()

        return render_template("edit.html", blog=blog, posts=posts)

@app.route("/dashboard/post/<name>", methods=['GET', 'POST'])
def new_post(name):
    if g.user is None:
        return redirect("/login")

    blog = g.db.query(Blog).filter_by(name=name).first()
    if blog is None:
        return redirect("/dashboard")

    if blog.owner != g.user:
        return redirect("/dashboard")

    if request.method == "GET":
       return render_template("new_post.html", blog=blog)
    elif request.method == "POST":
        u = g.db.query(User).filter_by(id=g.user).first()
        data = {}
        data['title'] = request.form.get('title')
        data['content'] = sanitize_html(request.form.get('content'))
        data['content_raw'] = request.form.get('content_raw')
        data['author'] = request.form.get('author')
        data['link'] = gen_link(data['title'])
        p = g.db.query(Post).filter(Post.link == data['link'], Post.blog == blog.id).count()
        if p > 0:
            data['link'] = data['link'] + "-" + str(p + 1)
        

        new_post = Post(blog=blog.id, title=data['title'], content_raw=data['content_raw'], content_html=data['content'], author=data['author'], link=data['link'])
        g.db.add(new_post)
        g.db.commit()

        return redirect('/dashboard/edit/' + blog.name)
   
    
@app.route("/dashboard/preview", methods=['POST'])
def preview():
    if g.user is None:
        return redirect("/login")

    u = g.db.query(User).filter_by(id=g.user).first()
    data = {}
    data['title'] = request.form.get('title')
    data['content'] = sanitize_html(request.form.get('content'))
    data['author'] = request.form.get('author')
    data['blog_title'] = request.form.get('blog_title')
    data['blog_name'] = request.form.get('blog_name')
    data['date'] = request.form.get('date')
    data['author_name'] = u.username
    return render_template("preview.html", data=data)

@app.route("/b/<blog>")
def show_blog(blog):
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect("/")

    if blog.access == "domain":
        return redirect(f"https://{blog.name}.{os.getenv('DOMAIN')}/")

    posts = g.db.query(Post).filter_by(blog=blog.id).all()

    return render_template("blog.html", blog=blog, posts=posts)

@app.route("/", subdomain="<blog>")
def show_subblog(blog):
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect(f"https://{os.getenv('DOMAIN')}/")

    if blog.access == "path":
        return redirect(f"https://{os.getenv('DOMAIN')}/b/{blog.name}")

    posts = g.db.query(Post).filter_by(blog=blog.id).all()

    return render_template("blog.html", blog=blog, posts=posts)   

@app.route("/b/<blog>/<post>")
def show_post(blog, post):
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect("/")

    if blog.access == "domain":
        return redirect(f"https://{blog.name}.{os.getenv('DOMAIN')}/{post.link}")
    one_post = g.db.query(Post).filter(Post.blog == blog.id, Post.link == post).first()
    user = g.db.query(User).filter_by(id=g.user)

    return render_template("post.html", user=user, blog=blog, post=one_post)

@app.route('/<post>', subdomain="<blog>")
def show_subport(blog, post):
    blog = g.db.query(Blog).filter_by(name=blog).first()
    if blog is None:
        return redirect(f"https://{os.getenv('DOMAIN')}/")

    if blog.access == "path":
        return redirect(f"https://{os.getenv('DOMAIN')}/b/{blog.name}/{post.link}")
    one_post = g.db.query(Post).filter(Post.blog == blog.id, Post.link == post).first()
    user = g.db.query(User).filter_by(id=g.user)

    return render_template("post.html", user=user, blog=blog, post=one_post)

@app.route("/")
def index():
    if g.user is not None:
        return redirect("/dashboard")
    
    return render_template('index.html')


if __name__ == "__main__":
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.run(host=os.environ.get("IP"), port=os.environ.get("PORT"))
