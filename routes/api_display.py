import os
import sqlite3

from flask import Blueprint, abort, jsonify, request, send_file

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
        "SELECT user_acro, user_time_offset, user_game_start_timestamp, is_displayed FROM users ORDER BY user_acro ASC"
    )
    rows = cursor_db.fetchall()
    connection_db.close()

    user_dict = {}
    for acro, offset, start, disp in rows:
        if int(disp) == 0:
            continue
        user_dict[acro] = count_remaining_time(start, offset)

    return user_dict


def get_announcements():
    """
    Returns list of visible announcements
    Format: [
        {"id": int, "for_display": str, "order": int, "data": str (base64 PNG), "visible": bool}
    ]
    """
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, for_display, "order", data, visible
        FROM announcements
        WHERE visible = 1
        ORDER BY "order" DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    announcements = [
        {
            "id": row[0],
            "for_display": row[1],
            "order": row[2] if row[2] is not None else 9999,
            "data": row[3],
            "visible": bool(row[4]),
        }
        for row in rows
    ]
    return announcements


@bp_display.route("/get_time_simple", methods=["GET"])
def get_time_simple():
    return jsonify(get_time_data())


@bp_display.route("/get_time", methods=["GET"])
def get_time():
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
        result.append({"name": name, "offset": offset, "start": start})
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
        return base64_data

    abort(400, description="Invalid format. Use 'png' or 'base64'.")


# -------------------
# ANNOUNCEMENTS API
# -------------------


@bp_display.route("/announcements", methods=["GET"])
def list_announcements():
    """List all announcements"""
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, for_display, "order", data, visible
        FROM announcements
        ORDER BY "order" ASC
    """
    )
    rows = cursor.fetchall()
    conn.close()

    announcements = [
        {
            "id": r[0],
            "for_display": r[1],
            "order": r[2],
            "data": r[3],
            "visible": bool(r[4]) if r[4] is not None else True,
        }
        for r in rows
    ]
    return jsonify(announcements)


@bp_display.route("/announcements", methods=["POST"])
def create_announcement():
    """Create new announcement"""
    data = request.get_json()
    if (
        not data
        or "for_display" not in data
        or "order" not in data
        or "data" not in data
    ):
        abort(400, description="Missing required fields")

    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    visible = data.get("visible", True)

    cursor.execute(
        'INSERT INTO announcements (for_display, "order", data, visible) VALUES (?, ?, ?, ?)',
        (data["for_display"], data["order"], data["data"], int(visible)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": new_id, **data}), 201


@bp_display.route("/announcements/<int:announcement_id>", methods=["PUT"])
def update_announcement(announcement_id):
    """Update announcement"""
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    fields = []
    values = []
    for field in ["for_display", "order", "data", "visible"]:
        if field in data:
            fields.append(f'"{field}" = ?')
            values.append(data[field] if field != "visible" else int(data[field]))

    if not fields:
        abort(400, description="No updatable fields provided")

    values.append(announcement_id)
    query = f"UPDATE announcements SET {', '.join(fields)} WHERE id = ?"

    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()

    return jsonify({"message": "Announcement updated"})


@bp_display.route("/announcements/<int:announcement_id>", methods=["DELETE"])
def delete_announcement(announcement_id):
    """Delete announcement"""
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Announcement deleted"})
