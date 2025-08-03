import os
import sqlite3

from flask import Blueprint, jsonify, request, send_file

import config
from db.helpers import insert_coin, insert_user
from display.engine_loader import load_display_engines
from utils.time_utils import count_new_offset, count_remaining_time

bp_display = Blueprint("display", __name__)


def get_time_data():
    """
    Returns user times as a dict {acro: remaining_time}.
    Can be used by both the API route and background loop.
    """
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()
    cursor_db.execute(
        "SELECT user_acro, user_time_offset, user_game_start_timestamp, is_displayed FROM users"
    )
    rows = cursor_db.fetchall()
    connection_db.close()

    user_dict = {}

    for acro, offset, start, disp in rows:
        if int(disp) == 0:
            continue
        user_dict[acro] = count_remaining_time(start, offset)

    return user_dict


@bp_display.route("/get_time_simple", methods=["GET"])
def get_time_simple():
    # reuse the same logic
    return jsonify(get_time_data())


@bp_display.route("/get_time", methods=["GET"])
def get_time():
    # reuse the same logic (kept identical for now)
    return jsonify(get_time_data())


@bp_display.route("/show_times", methods=["GET"])
def api_times_init():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute(
        """
        SELECT user_name, user_time_offset, user_game_start_timestamp, is_displayed
        FROM users
    """
    ).fetchall()
    connection_db.close()

    result = []
    for name, offset, start, is_disp in rows:
        if is_disp == 0:
            continue
        result.append(
            {"name": name, "offset": offset, "start": start}  # ISO format is fine
        )
    return jsonify(result)


@bp_display.route("/display_output/<display_name>", methods=["GET"])
def get_display_output(display_name):

    displays = load_display_engines()
    valid_names = [d["name"] for d in displays]
    if display_name not in valid_names:
        abort(404, description="Display not found")

    fmt = request.args.get("format", "png").lower()

    png_path = os.path.join(config.DISPLAY_STATE_DIR, f"{display_name}_current.png")
    dis_path = os.path.join(config.DISPLAY_STATE_DIR, f"{display_name}_current.dis")

    if fmt == "png":
        if not os.path.exists(png_path):
            abort(404, description="Display image not available")
        return send_file(png_path, mimetype="image/png")

    elif fmt == "base64":
        if not os.path.exists(dis_path):
            abort(404, description="Display frame not available")
        with open(dis_path, "r") as f:
            base64_data = f.read().strip()
        return jsonify({"display": display_name, "frame_base64": base64_data})

    abort(400, description="Invalid format. Use 'png' or 'base64'.")
