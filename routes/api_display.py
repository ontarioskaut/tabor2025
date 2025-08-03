import sqlite3

from flask import Blueprint, jsonify, request

import config
from db.helpers import insert_coin, insert_user
from utils.time_utils import count_new_offset, count_remaining_time

bp_display = Blueprint("display", __name__)


@bp_display.route("/get_time_simple", methods=["GET"])
def get_time_simple():
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

    return jsonify(user_dict)


@bp_display.route("/get_time", methods=["GET"])
# i thought i will do something about this, but then i just left it so it's the same as simple version
def get_time():
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

    return jsonify(user_dict)


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
