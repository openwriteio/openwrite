from flask import Blueprint, render_template, redirect, g
from openwrite.utils.models import Blog, User

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
def admin():
    if g.user is None or g.isadmin == 0:
        return redirect("/")

    blogs = g.db.query(Blog).all()
    users = g.db.query(User).all()

    return render_template("admin.html", blogs=blogs, users=users)

@admin_bp.route("/admin/delete_blog/<blog>")
def admin_delete_blog(blog):
    if g.user is None or g.isadmin == 0:
        return redirect("/")

    b = g.db.query(Blog).filter_by(name=blog).first()
    if b:
        g.db.delete(b)
        g.db.commit()

    return redirect("/admin")

@admin_bp.route("/admin/delete_user/<username>")
def admin_delete_user(username):
    if g.user is None or g.isadmin == 0:
        return redirect("/")

    user = g.db.query(User).filter_by(username=username).first()
    if not user:
        return redirect("/admin")

    user_blogs = g.db.query(Blog).filter_by(owner=user.id).all()
    for b in user_blogs:
        g.db.delete(b)

    g.db.delete(user)
    g.db.commit()

    return redirect("/admin")

