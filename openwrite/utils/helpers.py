import bleach
import re
import unicodedata
import hashlib
from flask import request, g
import os
import secrets
import json
import base64
import requests
import datetime
from urllib.parse import urlparse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from bs4 import BeautifulSoup


def sanitize_html(content):
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'hr',
        'strong', 'b', 'em', 'i', 'u',
        'ul', 'ol', 'li',
        'a', 'img', 'video',
        'code', 'pre', 'del',
        'blockquote',
        'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td'
    ]

    allowed_attrs = {
        'a': ['href', 'title', 'rel', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'th': ['align'],
        'td': ['align'],
        'video': ['src', 'width', 'height', 'controls']
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


def verify_http_signature(headers, body, blog):
    try:
        digest_header = headers.get("Digest")
        if not digest_header or not digest_header.startswith("SHA-256="):
            return False

        digest_b64 = digest_header.split("=", 1)[1]
        actual_digest = base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()
        if digest_b64 != actual_digest:
            return False

        sig_header = headers.get("Signature")
        if not sig_header:
            return False

        sig_parts = {}
        for part in sig_header.split(","):
            k, v = part.strip().split("=", 1)
            sig_parts[k] = v.strip('"')

        key_id = sig_parts.get("keyId")
        algorithm = sig_parts.get("algorithm")
        header_list = sig_parts.get("headers", "").split()
        signature_b64 = sig_parts.get("signature")

        if not key_id or not algorithm or not header_list or not signature_b64:
            return False

        string_lines = []
        for h in header_list:
            if h == "(request-target)":
                method = "post"
                path = f"/inbox/{blog}"
                string_lines.append(f"(request-target): {method} {path}")
            else:
                value = headers.get(h, "")
                string_lines.append(f"{h.lower()}: {value}")

        string_to_verify = "\n".join(string_lines)

        actor_url = key_id.split("#")[0]
        res = requests.get(actor_url, headers={"Accept": "application/activity+json"})
        actor_data = res.json()
        public_key_pem = actor_data["publicKey"]["publicKeyPem"]

        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        signature = base64.b64decode(signature_b64)

        public_key.verify(
            signature,
            string_to_verify.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return True

    except InvalidSignature:
        return False
    except Exception as e:
        return False

def send_activity(activity, private_key_pem, from_, to):

    body = json.dumps(activity)
    digest = "SHA-256=" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
    date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    to_actor = from_
    inbox_url = to
    parsed = urlparse(inbox_url)
    host = parsed.hostname
    path = parsed.path

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(), password=None
    )

    headers_to_sign = [
        f"(request-target): post {path}",
        f"host: {host}",
        f"date: {date}",
        f"digest: {digest}",
        "content-type: application/activity+json"
    ]
    string_to_sign = "\n".join(headers_to_sign)

    signature = private_key.sign(
        string_to_sign.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode()

    signature_header = (
        f'keyId="{to_actor}#main-key",'
        f'algorithm="rsa-sha256",'
        f'headers="(request-target) host date digest content-type",'
        f'signature="{signature_b64}"'
    )

    headers = {
        "Host": host,
        "Date": date,
        "Digest": digest,
        "Content-Type": "application/activity+json",
        "Signature": signature_header
    }
    #print(f"""
    #    URL:
    #    {inbox_url}

    #    Headers:
    #    {headers}

    #    Body:
    #    {body}
    #""")

    response = requests.post(inbox_url, headers=headers, data=body)
    #print(f"""
    #    [+] Sent to {inbox_url}: {response.status_code}
    #    Body:

    #    {response.text}
    #""")
    if response.status_code >= 400:
        print("[-] Response:", response.text)

    return response.status_code

def is_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return bool(soup.find())

def get_themes():
    css_files = [f.replace(".css", "") for f in os.listdir(f"{g.mainpath}/static/style/themes/") if f.endswith(".css")]

    return css_files

