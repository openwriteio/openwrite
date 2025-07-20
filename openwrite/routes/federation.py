from flask import Blueprint, render_template, redirect, g, jsonify, request, abort, Response
from openwrite.utils.models import Blog, User, Like, Post
from openwrite.utils.helpers import verify_http_signature, send_activity, anonymize
import json
import requests
from datetime import datetime, timezone

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

    published = b.created
    dt = datetime.strptime(str(published), "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")   

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
        "outbox": f"https://{g.main_domain}/outbox/{blog}",
        "followers": f"https://{g.main_domain}/followers/{blog}",
        "published": iso,
        "manuallyApprovesFollowers": False,
        "discoverable": True,
        "indexable": True,
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

    return Response(json.dumps(actor), content_type="application/activity+json", headers={
        'Cache-Control': 'max-age=3600',
        'Vary': 'Accept'
    })

@federation_bp.route("/activity/<blog>/create/<int:post_id>")
def activity_create(blog, post_id):
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)
    
    post = g.db.query(Post).filter_by(id=post_id, blog=b.id).first()
    if not post:
        abort(404)

    if b.access == "path":
        url = f"https://{g.main_domain}/b/{blog}"
    else:
        url = f"https://{blog}.{g.main_domain}"

    dt = datetime.strptime(str(post.date), "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")

    create_activity = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"https://{g.main_domain}/activity/{blog}/create/{post.id}",
        "type": "Create",
        "actor": f"https://{g.main_domain}/activity/{blog}",
        "published": iso,
        "to": ["https://www.w3.org/ns/activitystreams#Public"],
        "cc": [f"https://{g.main_domain}/followers/{blog}"],
        "object": {
            "id": f"https://{g.main_domain}/activity/{blog}/posts/{post.id}",
            "type": "Note",
            "summary": None,
            "attributedTo": f"https://{g.main_domain}/activity/{blog}",
            "content": f"<h3>{post.title}</h3><p><a href=\"{url}/{post.link}\">{url}/{post.link}</a></p>",
            "published": iso,
            "url": f"{url}/{post.link}",
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [f"https://{g.main_domain}/followers/{blog}"],
            "sensitive": False,
            "atomUri": f"https://{g.main_domain}/activity/{blog}/posts/{post.id}",
            "attachment": [],
            "tag": []
        }
    }

    return Response(json.dumps(create_activity), content_type="application/activity+json", headers={
        'Cache-Control': 'max-age=3600',
        'Vary': 'Accept'
    })

@federation_bp.route("/activity/<blog>/posts/<int:post_id>")
def activity_post(blog, post_id):
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)
    
    post = g.db.query(Post).filter_by(id=post_id, blog=b.id).first()
    if not post:
        abort(404)

    if b.access == "path":
        url = f"https://{g.main_domain}/b/{blog}"
    else:
        url = f"https://{blog}.{g.main_domain}"

    dt = datetime.strptime(str(post.date), "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")

    note = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"https://{g.main_domain}/activity/{blog}/posts/{post.id}",
        "type": "Note",
        "summary": None,
        "attributedTo": f"https://{g.main_domain}/activity/{blog}",
        "content": f"<h3>{post.title}</h3><p><a href=\"{url}/{post.link}\">{url}/{post.link}</a></p>",
        "published": iso,
        "url": f"{url}/{post.link}",
        "to": ["https://www.w3.org/ns/activitystreams#Public"],
        "cc": [f"https://{g.main_domain}/followers/{blog}"],
        "sensitive": False,
        "atomUri": f"https://{g.main_domain}/activity/{blog}/posts/{post.id}",
        "attachment": [],
        "tag": []
    }

    return Response(json.dumps(note), content_type="application/activity+json", headers={
        'Cache-Control': 'max-age=3600',
        'Vary': 'Accept'
    })

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
        id_ = data.get("id")

        if object_ != f"https://{g.main_domain}/activity/{blog}":
            return "Invalid target", 400

        followers = []
        if b.followers not in (None, "null", "NULL"):
            followers = json.loads(b.followers)
        if actor not in followers:
            followers.append(actor)
        b.followers = json.dumps(followers)
        g.db.commit()

        activity = {
          "@context": "https://www.w3.org/ns/activitystreams",
          "id": f"https://{g.main_domain}/activity/{blog}#accept-{id_.split('/')[-1]}",
          "type": "Accept",
          "actor": f"https://{g.main_domain}/activity/{blog}",
          "object": data,
          "to": [f"{actor}"]
        }
        
        actor_doc = requests.get(actor, headers={"Accept": "application/activity+json"}).json()
        inbox = actor_doc.get("endpoints", {}).get("sharedInbox", actor)

        from_ = f"https://{g.main_domain}/activity/{blog}"
        send_activity(activity, b.priv_key, from_, f"{actor}/inbox")

        return "", 202

    elif data.get("type") == "Undo":
        actor = data.get("actor")
        object_ = data.get("object")
        
        if object_['type'] == "Follow":
            if object_['object'] != f"https://{g.main_domain}/activity/{blog}":
                return "Invalid target", 400

            followers = []
            if b.followers not in (None, "null", "NULL"):
                followers = json.loads(b.followers)
            if actor in followers:
                followers = followers.remove(actor)
            b.followers = json.dumps(followers)
            g.db.commit()

        elif object_['type'] == "Like":
            post_name = object_['object'].split("/")[-1]
            if object_['object'].split("/")[2] == g.main_domain:
                blog_name = object_['object'].split("/")[-2]
            else:
                blog_name = object_['object'].split("/")[2].split('.')[0]
            blog = g.db.query(Blog).filter_by(name=blog_name).first()
            blog_id = blog.id
            post = g.db.query(Post).filter(Post.blog == blog_id, Post.link == post_name).first()
            post_id = post.id

            hashed = anonymize(actor)
            like = g.db.query(Like).filter(Like.blog == blog_id, Like.post == post_id, Like.hash == hashed).first()
            g.db.delete(like)
            g.db.commit()
        
        return "", 202

    elif data.get("type") == "Like":
        object_ = data.get("object")
        actor = data.get("actor")
        post_name = object_.split("/")[-1]
        if object_.split("/")[2] == g.main_domain:
            blog_name = object_.split("/")[-2]
        else:
            blog_name = object_.split("/")[2].split('.')[0]
        blog = g.db.query(Blog).filter_by(name=blog_name).first()
        blog_id = blog.id
        post = g.db.query(Post).filter(Post.blog == blog_id, Post.link == post_name).first()
        post_id = post.id

        hashed = anonymize(actor)
        like = Like(hash=hashed, blog=blog_id, post=post_id)
        g.db.add(like)
        g.db.commit()

    return "", 202

@federation_bp.route("/outbox/<blog>")
def outbox(blog):
    page = request.args.get("page")
    
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    p = g.db.query(Post).filter_by(blog=b.id).order_by(Post.date.desc())
    total = p.count()
    posts = p.all()
    
    first_outbox = {
      "@context": "https://www.w3.org/ns/activitystreams",
      "id": f"https://{g.main_domain}/outbox/{blog}",
      "type": "OrderedCollection",
      "totalItems": total,
      "first": f"https://{g.main_domain}/outbox/{blog}?page=true"
    }

    if not page:
        if total <= 10:
            orderedPosts = []
            if b.access == "path":
                url = f"https://{g.main_domain}/b/{blog}"
            else:
                url = f"https://{blog}.{g.main_domain}"
            
            for post in posts:
                dt = datetime.strptime(str(post.date), "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")   
                orderedPosts.append({
                    "id": f"https://{g.main_domain}/activity/{blog}/create/{post.id}",
                    "type": "Create",
                    "actor": f"https://{g.main_domain}/activity/{blog}",
                    "published": iso,
                    "to": ["https://www.w3.org/ns/activitystreams#Public"],
                    "cc": [f"https://{g.main_domain}/followers/{blog}"],
                    "object": {
                        "id": f"https://{g.main_domain}/activity/{blog}/posts/{post.id}",
                        "type": "Note",
                        "attributedTo": f"https://{g.main_domain}/activity/{blog}",
                        "content": f"<p><strong>{post.title}</strong></p><p><a href=\"{url}/{post.link}\">{url}/{post.link}</a></p>",
                        "published": iso,
                        "url": f"{url}/{post.link}",
                        "to": ["https://www.w3.org/ns/activitystreams#Public"],
                        "cc": [f"https://{g.main_domain}/followers/{blog}"],
                        "sensitive": False
                    }
                })
            
            first_outbox["orderedItems"] = orderedPosts
            
            return Response(json.dumps(first_outbox), content_type="application/activity+json; charset=utf-8", headers={
                'Cache-Control': 'max-age=300',
                'Vary': 'Accept'
            })
        else:
            return Response(json.dumps(first_outbox), content_type="application/activity+json; charset=utf-8", headers={
                'Cache-Control': 'max-age=300',
                'Vary': 'Accept'
            })

    orderedPosts = []
    if b.access == "path":
        url = f"https://{g.main_domain}/b/{blog}"
    else:
        url = f"https://{blog}.{g.main_domain}"
    for post in posts:
        dt = datetime.strptime(str(post.date), "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        iso = dt.isoformat(timespec="seconds").replace("+00:00", "Z")   
        orderedPosts.append({
            "id": f"https://{g.main_domain}/activity/{blog}/create/{post.id}",
            "type": "Create",
            "actor": f"https://{g.main_domain}/activity/{blog}",
            "published": iso,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [f"https://{g.main_domain}/followers/{blog}"],
            "object": {
                "id": f"https://{g.main_domain}/activity/{blog}/posts/{post.id}",
                "type": "Note",
                "summary": None,
                "attributedTo": f"https://{g.main_domain}/activity/{blog}",
                "content": f"<h3>{post.title}</h3><p><a href=\"{url}/{post.link}\">{url}/{post.link}</a></p>",
                "published": iso,
                "url": f"{url}/{post.link}",
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [f"https://{g.main_domain}/followers/{blog}"],
                "sensitive": False,
                "atomUri": f"https://{g.main_domain}/activity/{blog}/posts/{post.id}",
                "attachment": [],
                "tag": []
            }
        })

    outbox = {
      "@context": [
        "https://www.w3.org/ns/activitystreams",
        {
          "ostatus": "http://ostatus.org#",
          "atomUri": "ostatus:atomUri",
          "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
          "conversation": "ostatus:conversation",
          "sensitive": "as:sensitive",
          "toot": "http://joinmastodon.org/ns#",
          "votersCount": "toot:votersCount"
        }
      ],
      "id": f"https://{g.main_domain}/outbox/{blog}?page={page}",
      "type": "OrderedCollectionPage",
      "partOf": f"https://{g.main_domain}/outbox/{blog}",
      "orderedItems": orderedPosts
    }

    return Response(json.dumps(outbox), content_type="application/activity+json", headers={
        'Cache-Control': 'max-age=300',
        'Vary': 'Accept'
    })

@federation_bp.route("/followers/<blog>")
def followers(blog):
    page = request.args.get("page")
    b = g.db.query(Blog).filter_by(name=blog).first()
    if not b:
        abort(404)

    followers = []
    if b.followers not in (None, "null", "NULL"):
        followers = json.loads(b.followers)

    if page not in ("true", "1"):
        data = {
          "@context": "https://www.w3.org/ns/activitystreams",
          "id": f"https://{g.main_domain}/followers/{blog}",
          "type": "OrderedCollection",
          "totalItems": len(followers),
          "first": {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": f"https://{g.main_domain}/followers/{blog}?page=true",
            "type": "OrderedCollectionPage",
            "partOf": f"https://{g.main_domain}/followers/{blog}",
            "totalItems": len(followers),
            "orderedItems": followers
          }
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
