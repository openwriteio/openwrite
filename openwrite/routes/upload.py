from flask import Blueprint, request, jsonify, g, send_from_directory, abort
from openwrite.utils.models import User
from werkzeug.utils import secure_filename
from PIL import Image
import os
import hashlib
import requests

upload_bp = Blueprint("upload", __name__)

UPLOAD_ENABLED = os.getenv("MEDIA_UPLOAD", "no") == "yes"
STORAGE_BACKEND = os.getenv("UPLOAD_STORAGE", "local")
BUNNY_API_KEY = os.getenv("BUNNY_API_KEY")
BUNNY_ZONE = os.getenv("BUNNY_STORAGE_ZONE")
BUNNY_URL = os.getenv("BUNNY_STORAGE_URL")
LOCAL_UPLOAD_DIR = os.getenv("UPLOAD_PATH", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

@upload_bp.route("/upload_image", methods=["POST"])
def upload_image():
    if not UPLOAD_ENABLED:
        return jsonify({"error": g.trans['uploads_disabled']}), 403

    if 'file' not in request.files:
        return jsonify({"error": g.trans['no_file']}), 400

    if g.user is None:
        return jsonify({"error": "unauthorized"}), 403

    file = request.files['file']
    filename = file.filename
    if "." not in filename:
        return jsonify({"error": g.trans['invalid_filename']}), 400

    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({"error": g.trans['unsupported_filetype']}), 400

    try:
        img = Image.open(file.stream)
        img.verify()
    except Exception:
        return jsonify({"error": g.trans['not_image']}), 400

    file.stream.seek(0)
    user = g.db.query(User).filter_by(id=g.user).first()

    m = hashlib.md5()
    m.update(filename.encode() + user.username.encode())
    filename = f"{user.username}_{m.hexdigest()}.{extension}"

    if STORAGE_BACKEND == "bunny":
        url = f"https://storage.bunnycdn.com/{BUNNY_ZONE}/{filename}"
        headers = {
            "AccessKey": BUNNY_API_KEY,
            "Content-Type": "application/octet-stream",
            "accept": "application/json"
        }
        response = requests.put(url, headers=headers, data=file)
        if response.ok:
            return jsonify({"url": f"{BUNNY_URL}{filename}"})
        else:
            return jsonify({"error": g.trans['upload_failed'], "detail": response.text}), 500

    elif STORAGE_BACKEND == "local":
        os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(LOCAL_UPLOAD_DIR, filename)
        file.save(filepath)
        return jsonify({"url": f"/uploads/{filename}"})

    return jsonify({"error": g.trans['upload_failed']}), 500

@upload_bp.route("/uploads/<file>")
def get_file(file):
    filename = secure_filename(file)
    filepath = os.path.join(LOCAL_UPLOAD_DIR, filename)

    if not os.path.isfile(filepath):
        abort(404)

    return send_from_directory(LOCAL_UPLOAD_DIR, filename)
