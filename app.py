import asyncio
import hmac
from functools import wraps
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import Config
from models import Channel, Subscription, db_session, init_db
from services.log_service import log_service
from services.subscription_service import subscription_service


def parse_message_limit(value) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        return Config.DEFAULT_MESSAGE_LIMIT

    return max(1, min(limit, Config.MAX_MESSAGE_LIMIT))


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def telegram_session_exists() -> bool:
    return Path(f"{Config.TELEGRAM_SESSION}.session").exists()


def create_app() -> Flask:
    Config.validate()
    init_db()

    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    @flask_app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            username_ok = hmac.compare_digest(username, Config.ADMIN_USERNAME or "")
            password_ok = hmac.compare_digest(password, Config.ADMIN_PASSWORD or "")

            if username_ok and password_ok:
                session["logged_in"] = True
                flash("Welcome back.", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid credentials.", "danger")

        return render_template("login.html")

    @flask_app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "info")
        return redirect(url_for("login"))

    @flask_app.route("/")
    @login_required
    def home():
        return redirect(url_for("dashboard"))

    @flask_app.route("/dashboard")
    @login_required
    def dashboard():
        with db_session() as db:
            subscriptions = db.query(Subscription).order_by(Subscription.id.desc()).all()
            dashboard_subs = [
                {
                    "id": sub.id,
                    "name": sub.name,
                    "token": sub.token,
                    "channels": sub.channels,
                }
                for sub in subscriptions
            ]

            return render_template(
                "dashboard.html",
                total_channels=db.query(Channel).count(),
                enabled_channels=db.query(Channel).filter(Channel.enabled.is_(True)).count(),
                total_subscriptions=len(subscriptions),
                telegram_connected=telegram_session_exists(),
                subscriptions=dashboard_subs,
            )

    @flask_app.route("/channels")
    @login_required
    def channels():
        with db_session() as db:
            all_channels = db.query(Channel).order_by(Channel.id.desc()).all()
            return render_template("channels.html", channels=all_channels)

    @flask_app.route("/channels/add", methods=["POST"])
    @login_required
    def add_channel():
        name = request.form.get("channel_name", "").strip()
        if not name:
            flash("Channel name required.", "danger")
            return redirect(url_for("channels"))

        with db_session() as db:
            exists = db.query(Channel).filter(Channel.name == name).first()
            if exists:
                flash("Channel already exists.", "warning")
                return redirect(url_for("channels"))

            db.add(Channel(name=name))
            db.commit()

        flash("Channel added.", "success")
        return redirect(url_for("channels"))

    @flask_app.route("/channels/<int:channel_id>/enable", methods=["POST"])
    @login_required
    def enable_channel(channel_id):
        return set_channel_enabled(channel_id, True)

    @flask_app.route("/channels/<int:channel_id>/disable", methods=["POST"])
    @login_required
    def disable_channel(channel_id):
        return set_channel_enabled(channel_id, False)

    def set_channel_enabled(channel_id: int, enabled: bool):
        with db_session() as db:
            channel = db.query(Channel).filter(Channel.id == channel_id).first()
            if not channel:
                flash("Channel not found.", "warning")
                return redirect(url_for("channels"))

            channel.enabled = enabled
            db.commit()

        flash(
            "Channel enabled." if enabled else "Channel disabled.",
            "success" if enabled else "warning",
        )
        return redirect(url_for("channels"))

    @flask_app.route("/channels/<int:channel_id>/delete", methods=["POST"])
    @login_required
    def delete_channel(channel_id):
        with db_session() as db:
            channel = db.query(Channel).filter(Channel.id == channel_id).first()
            if not channel:
                flash("Channel not found.", "warning")
                return redirect(url_for("channels"))

            db.delete(channel)
            db.commit()

        flash("Channel deleted.", "success")
        return redirect(url_for("channels"))

    @flask_app.route("/subscriptions")
    @login_required
    def subscriptions():
        with db_session() as db:
            enabled_channels = (
                db.query(Channel).filter(Channel.enabled.is_(True)).order_by(Channel.name).all()
            )
            subscriptions = db.query(Subscription).order_by(Subscription.id.desc()).all()

            return render_template(
                "subscriptions.html",
                channels=enabled_channels,
                subscriptions=subscriptions,
            )

    @flask_app.route("/subscriptions/create", methods=["POST"])
    @login_required
    def create_subscription():
        name = request.form.get("name", "").strip()
        channel_ids = request.form.getlist("channel_ids")

        if not name:
            flash("Name required.", "danger")
            return redirect(url_for("subscriptions"))
        if not channel_ids:
            flash("Select at least one channel.", "danger")
            return redirect(url_for("subscriptions"))

        try:
            subscription_service.create_subscription(
                name=name,
                channel_ids=channel_ids,
                remark_name=request.form.get("remark_name", "").strip(),
                base64_enabled=request.form.get("base64_enabled") == "1",
                message_limit=parse_message_limit(request.form.get("message_limit")),
            )
        except Exception as exc:
            log_service.exception(exc)
            flash(str(exc), "danger")
        else:
            flash("Subscription created.", "success")

        return redirect(url_for("subscriptions"))

    @flask_app.route(
        "/subscriptions/<int:sub_id>/edit",
        methods=["POST"],
    )
    @login_required
    def edit_subscription(sub_id):

        name = request.form.get("name", "").strip()

        channel_ids = request.form.getlist("channel_ids")

        if not name:
            flash("Name required.", "danger")
            return redirect(url_for("subscriptions"))

        if not channel_ids:
            flash(
                "Select at least one channel.",
                "danger",
            )
            return redirect(url_for("subscriptions"))

        try:

            subscription_service.update_subscription(
                subscription_id=sub_id,
                name=name,
                channel_ids=channel_ids,
                remark_name=request.form.get(
                    "remark_name",
                    "",
                ).strip(),
                base64_enabled=request.form.get("base64_enabled") == "1",
                message_limit=parse_message_limit(request.form.get("message_limit")),
            )

        except Exception as exc:

            log_service.exception(exc)

            flash(str(exc), "danger")

        else:

            flash(
                "Subscription updated.",
                "success",
            )

        return redirect(url_for("subscriptions"))

    @flask_app.route("/subscriptions/<int:sub_id>/delete", methods=["POST"])
    @login_required
    def delete_subscription(sub_id):
        if subscription_service.delete_subscription(sub_id):
            flash("Subscription deleted.", "success")
        else:
            flash("Subscription not found.", "warning")

        return redirect(url_for("subscriptions"))

    @flask_app.route("/subscriptions/<int:sub_id>/refresh", methods=["POST"])
    @login_required
    def refresh_subscription(sub_id):
        try:
            configs = asyncio.run(subscription_service.build_subscription(sub_id))
        except Exception as exc:
            log_service.exception(exc)
            flash(str(exc), "danger")
        else:
            flash(f"Refresh successful. Found {len(configs)} configs.", "success")

        return redirect(url_for("subscriptions"))

    @flask_app.route("/sub/<token>")
    def subscription_feed(token):
        feed_settings = subscription_service.get_feed_settings(token)
        if not feed_settings:
            return "Subscription not found", 404

        try:
            content = asyncio.run(
                subscription_service.build_feed(
                    feed_settings["id"],
                    feed_settings["base64_enabled"],
                )
            )
        except Exception as exc:
            log_service.exception(exc)
            return "Subscription error", 500

        return content, 200, {"Content-Type": "text/plain; charset=utf-8"}

    @flask_app.route("/logs")
    @login_required
    def logs():
        return render_template("logs.html", logs=log_service.get_logs())

    @flask_app.route("/logs/clear", methods=["POST"])
    @login_required
    def clear_logs():
        log_service.clear_logs()
        flash("Logs cleared.", "success")
        return redirect(url_for("logs"))

    return flask_app


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
