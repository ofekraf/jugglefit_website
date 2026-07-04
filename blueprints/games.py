from flask import Blueprint, render_template, request, jsonify

from pylib.auth import current_user, login_required_user
from pylib.classes.prop import Prop, MAIN_PROPS
from pylib.rating.need import compute_needs, GAME_META
from pylib.rating.pair_picker import build_set, AVAILABLE_GAMES
from pylib.rating.answer import handle_answer
from pylib.rating.flags import record_flag
from pylib.rating.progress import me_payload
from pylib.rating.promote import _annotate as _annotate_candidate_row  # readiness for submissions
from pylib.rating.totd import pick as totd_pick, yesterday_summary as totd_yesterday
from pylib.configuration.consts import (
    FLAG_REASONS, BADGES, HUB_LEADERBOARD_KIND, HUB_LEADERBOARD_PERIOD,
    HUB_LEADERBOARD_N,
)
from database.db_manager import db_manager
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
    focus = request.args.get("focus", type=int)
    try:
        tasks = build_set(game, prop, user_id=user.id, focus=focus)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    totd = totd_pick(prop)
    return jsonify({
        "prop": prop, "game": game, "tasks": tasks,
        "totd_id": totd["id"] if totd else None,
    })


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
    prop = _prop_arg()
    if not user:
        return jsonify({"logged_in": False, "prop": prop,
                        "badge_meta": {k: {"label": l, "emoji": e, "desc": d}
                                       for k, (l, e, d) in BADGES.items()}})
    return jsonify(me_payload(user, prop=prop))


@games_api.route("/totd")
def totd():
    prop = _prop_arg()
    return jsonify({
        "prop": prop,
        "yesterday": totd_yesterday(prop),
    })


@games_api.route("/me/submissions")
@login_required_user
def my_submissions():
    user = current_user()
    out = []
    for c in db_manager.user_submissions(user.id):
        row = {
            "id": c["id"],
            "prop_type": c["prop_type"],
            "props_count": c["props_count"],
            "name": c["name"],
            "siteswap_x": c["siteswap_x"],
            "status": c["status"],
        }
        if c["status"] == "active":
            a = _annotate_candidate_row(c)
            row.update({
                "readiness": a["readiness"],
                "gates": a["gates"],
                "gates_passed": a["gates_passed"],
                "share_url": f"/contribute/games/harder?prop={c['prop_type']}&focus={c['id']}",
            })
        out.append(row)
    return jsonify({"submissions": out})


@games_api.route("/hub_leaderboard")
def hub_leaderboard():
    from pylib.rating.leaderboard import get_board
    user = current_user()
    board = get_board(HUB_LEADERBOARD_KIND, HUB_LEADERBOARD_PERIOD,
                      viewer_id=user.id if user else None)
    board["top"] = board["top"][:HUB_LEADERBOARD_N]
    return jsonify(board)
