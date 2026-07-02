from flask import Blueprint, render_template, request, jsonify

from pylib.auth import current_user, login_required_user
from pylib.classes.prop import Prop, MAIN_PROPS
from pylib.rating.need import compute_needs, GAME_META
from pylib.rating.pair_picker import build_set, AVAILABLE_GAMES
from pylib.rating.answer import handle_answer
from pylib.rating.flags import record_flag
from pylib.configuration.consts import FLAG_REASONS
from hardcoded_database.tricks import ALL_PROPS_SETTINGS_JSON


games_bp = Blueprint("games", __name__, url_prefix="/contribute/games")
games_api = Blueprint("games_api", __name__, url_prefix="/api/games")


def _prop_arg(default: str = "balls") -> str:
    raw = request.args.get("prop", default)
    try:
        Prop.get_key_by_value(raw)
        return raw
    except Exception:
        return default


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------
@games_bp.route("/")
def hub():
    return render_template(
        "games/hub.html",
        props_settings=ALL_PROPS_SETTINGS_JSON,
        main_props=MAIN_PROPS,
        selected_prop=_prop_arg(),
        game_meta=GAME_META,
    )


def _game_ctx() -> dict:
    return dict(
        props_settings=ALL_PROPS_SETTINGS_JSON,
        main_props=MAIN_PROPS,
        selected_prop=_prop_arg(),
        FLAG_REASONS=FLAG_REASONS,
    )


@games_bp.route("/harder")
@login_required_user
def harder():
    return render_template("games/harder.html", **_game_ctx())


@games_bp.route("/tagging")
@login_required_user
def tagging():
    return render_template("games/tagging.html", **_game_ctx())


@games_bp.route("/throw")
@login_required_user
def throw():
    return render_template("games/throw.html", **_game_ctx())


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@games_api.route("/needs")
def needs():
    prop = _prop_arg()
    data = [n.to_dict() for n in compute_needs(prop, available_games=AVAILABLE_GAMES)]
    return jsonify({"prop": prop, "games": data})


@games_api.route("/<game>/next_set")
@login_required_user
def next_set(game: str):
    prop = _prop_arg()
    user = current_user()
    try:
        tasks = build_set(game, prop, user_id=user.id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"prop": prop, "game": game, "tasks": tasks})


@games_api.route("/answer", methods=["POST"])
@login_required_user
def answer():
    body = request.get_json(silent=True) or {}
    task_id = body.get("task_id")
    payload = body.get("payload") or {}
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    user = current_user()
    try:
        result = handle_answer(
            task_id, payload,
            user_id=user.id, anon_id=None,
            reliability=user.reliability,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(result)


@games_api.route("/flag", methods=["POST"])
def flag():
    user = current_user()
    if user is None:
        return jsonify({"error": "login_required"}), 401
    body = request.get_json(silent=True) or {}
    task_id = body.get("task_id")
    reason = body.get("reason")
    if not task_id:
        return jsonify({"error": "task_id required"}), 400
    try:
        results = record_flag(task_id=task_id, reason=reason,
                              user_id=user.id, is_admin=user.is_admin)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({
        "ok": True,
        "results": [r.__dict__ for r in results],
        "removed_any": any(r.removed for r in results),
    })


@games_api.route("/me")
def me():
    user = current_user()
    if not user:
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in": True,
        "display_name": user.display_name,
        "n_harder": user.n_harder,
        "n_tagging": user.n_tagging,
        "n_throw": user.n_throw,
        "n_tricks_promoted": user.n_tricks_promoted,
        "reliability": round(user.reliability, 3),
    })
