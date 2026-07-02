import time

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from pylib.auth import (
    register, authenticate, AuthError, login_user, logout_user, current_user,
    login_required_user, is_super_admin_credentials, ensure_super_admin_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _safe_next(target: str | None) -> str:
    # Only allow same-site relative paths.
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("home")


@auth_bp.route("/register", methods=["GET", "POST"])
def register_view():
    if request.method == "POST":
        name = request.form.get("display_name", "")
        pw = request.form.get("password", "")
        pw2 = request.form.get("password2", "")
        if pw != pw2:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html", display_name=name)
        try:
            user = register(name, pw)
        except ValueError as e:
            flash(str(e), "error")
            return render_template("auth/register.html", display_name=name)
        login_user(user)
        flash(f"Welcome, {user.display_name}!", "success")
        return redirect(_safe_next(request.args.get("next")))
    return render_template("auth/register.html", display_name="")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("display_name", "")
        pw = request.form.get("password", "")
        if is_super_admin_credentials(name, pw):
            user = ensure_super_admin_user()
            login_user(user)
            session["super_admin_at"] = time.time()
            return redirect(_safe_next(request.args.get("next")))
        try:
            user = authenticate(name, pw)
        except AuthError as e:
            flash(str(e), "error")
            return render_template("auth/login.html", display_name=name)
        login_user(user)
        return redirect(_safe_next(request.args.get("next")))
    return render_template("auth/login.html", display_name="")


@auth_bp.route("/logout")
def logout():
    logout_user()
    session.pop("super_admin_at", None)
    return redirect(url_for("home"))


@auth_bp.route("/profile")
@login_required_user
def profile():
    return render_template("auth/profile.html", user=current_user())
