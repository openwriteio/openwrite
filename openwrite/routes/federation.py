from flask import Blueprint, render_template, redirect, g, jsonify, request, abort, Response
from openwrite.utils.models import Blog, User
from openwrite.utils.helpers import verify_http_signature
import json

federation_bp = Blueprint("federation", __name__) 

@federation_bp.route("/.well-known/webfinger")
def webfinger():
    resource = request.args.get("resource")
    if not resource or not resource.startswith("acct:"):
        abort(400)

    blogname = resource.split(":")[1].split("@")[0]
    b_count = g.db.query(Blog).filter_by(name=blogname).count()
    if not b_count or b_count < 1:
        abort(404)
    data = {
        "subject": f"acct:{blogname}@{g.main_domain}",
        "links": [{
            "rel": "self",
            "type": "application/activity+json",
            "href": f"https://{g.main_domain}/activity/{blogname}"
        }]
    }

    return Response(
        response=json.dumps(data),
        status=200,
        content_type="application/jrd+json"
    )

@federation_bp.route("/activity/<blog>")
def activity(blog):
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    if b.access == "domain":
        url = f"https://{blog}.{g.main_domain}"
    else:
        url = f"https://{g.main_domain}/b/{blog}"
    actor = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            "https://w3id.org/security/v1"
        ],
        "id": f"https://{g.main_domain}/activity/{blog}",
        "type": "Person",
        "preferredUsername": blog,
        "name": blog,
        "summary": f"{blog} - Blog on {g.main_domain}",
        "inbox": f"https://{g.main_domain}/inbox/{blog}",
        "followers": f"https://{g.main_domain}/followers/{blog}",
        "url": url,
        "publicKey": {
            "id": f"https://{g.main_domain}/activity/{blog}#main-key",
            "owner": f"https://{g.main_domain}/activity/{blog}",
            "publicKeyPem": b.pub_key
        },
        "icon": {
            "type": "Image",
            "mediaType": "image/png",
            "url": f"https://{g.main_domain}/static/avatar.png"
        }
    }

    return Response(json.dumps(actor), content_type="application/activity+json")

@federation_bp.route("/inbox/<blog>", methods=["POST"])
def inbox(blog):
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    data = request.get_json()
    if not data:
        return "Bad Request", 400

    body = request.get_data(as_text=True)
    sign = verify_http_signature(request.headers, body, blog)
    if not sign:
        return "Bad signature", 400
    if data.get("type") == "Follow":
        actor = data.get("actor")
        object_ = data.get("object")

        if object_ != f"https://{g.main_domain}/activity/{blog}":
            return "Invalid target", 400

        followers = []
        if b.followers:
            followers = json.loads(b.followers)
        if actor not in followers:
            followers.append(actor)
        b.followers = json.dumps(followers)
        g.db.commit()

        return "", 202

    elif data.get("type") == "Undo":
        actor = data.get("actor")
        object_ = data.get("object")
        
        if object_['object'] != f"https://{g.main_domain}/activity/{blog}":
            return "Invalid target", 400

        followers = []
        if b.followers:
            followers = json.loads(b.followers)
        if actor in followers:
            followers = followers.remove(actor)
        b.followers = followers
        g.db.commit()

        return "", 202

    return "", 202


@federation_bp.route("/followers/<blog>")
def followers(blog):
    page = request.args.get("page")
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    followers = []
    if b.followers:
        followers = json.loads(b.followers)

    if not page:
        data = {
          "@context": "https://www.w3.org/ns/activitystreams",
          "id": f"https://{g.main_domain}/followers/{blog}",
          "type": "OrderedCollection",
          "totalItems": len(followers),
          "first": f"https://{g.main_domain}/followers/{blog}?page=1"
        }

        return Response(json.dumps(data), content_type="application/activity+json")

    data = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "id": f"https://{g.main_domain}/followers/{blog}?page={page}",
      "type": "OrderedCollectionPage",
      "totalItems": len(followers),
      "partOf": f"https://{g.main_domain}/followers/{blog}",
      "orderedItems": followers
    }

    return Response(json.dumps(data), content_type="application/activity+json")
