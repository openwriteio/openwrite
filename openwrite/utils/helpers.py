import bleach
import re
import unicodedata
import hashlib
from flask import request
import os
import secrets


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

    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)


def gen_link(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '-', text.strip())
    return text


def get_ip():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip


def anonymize(ip: str, salt: str = None) -> str:
    if salt is None:
        salt = os.getenv("SECRET_KEY", "")
    data = (salt + ip).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def safe_css(data):
    banned_keywords = [
        r"url\s*\(", r"@import", r"@keyframes", r"expression\s*\(", r"javascript\s*:", r"animation"
    ]

    for keyword in banned_keywords:
        data = re.sub(keyword, "", data, flags=re.IGNORECASE)

    return data

def generate_nonce():
    return secrets.token_urlsafe(16)
