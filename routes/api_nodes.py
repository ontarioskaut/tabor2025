import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, request

import config
from db.helpers import insert_coin, insert_user
from utils.time_utils import (count_new_offset, count_new_time,
                              count_remaining_time)

bp_nodes = Blueprint("nodes", __name__)


def addition_of_time(user_tag_id, time_to_change, mode: str = "+"):
    if not time_to_change or not user_tag_id:
        return jsonify({"error": "time_to_subtract and user_tag_id are required"}), 400

    try:
        time_to_change = int(time_to_change)
    except ValueError:
        return jsonify({"error": "time must be an integer"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute(
        "SELECT user_time_offset, user_game_start_timestamp FROM users WHERE user_tag_id = ?",
        (user_tag_id,),
    )
    user = cursor_db.fetchone()

    if user:
        current_offset, start_time = user
        # new_offset = count_new_offset(current_offset, time_to_change, mode)
        new_offset = count_new_time(current_offset, start_time, time_to_change, mode)
        cursor_db.execute(
            "UPDATE users SET user_time_offset = ? WHERE user_tag_id = ?",
            (new_offset, user_tag_id),
        )
        connection_db.commit()
        connection_db.close()

        time = count_remaining_time(start_time, new_offset)
        return jsonify({"status": "success", "user_time": time})
    else:
        connection_db.close()
        return jsonify({"error": "User not found"}), 404


def is_user_tag(tag_id):
    connection = sqlite3.connect(config.DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_tag_id = ?", (tag_id,))
    result = cursor.fetchone()
    connection.close()
    return result is not None


@bp_nodes.route("/search_tags", methods=["GET"])
def search_tags():
    tag_id = request.args.get("tag_id")

    if not tag_id:
        return jsonify({"error": "tag_id is required"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    # --- Check users ---
    cursor_db.execute(
        """
        SELECT user_id, user_name, user_acro, user_time_offset, user_game_start_timestamp
        FROM users
        WHERE user_tag_id = ?
        """,
        (tag_id,),
    )
    user = cursor_db.fetchone()

    if user:
        usr_id, user_name, user_acro, offset, start_ts = user
        remaining_time = count_remaining_time(start_ts, offset)

        connection_db.close()
        return jsonify(
            {
                "id": usr_id,
                "type": "user",
                "user_name": user_name,
                "remaining_time": remaining_time,
                "user_acro": user_acro,
                "coin_value": None,
                "active": None,
                "coin_category_name": None,
            }
        )

    # --- Check coins ---
    cursor_db.execute(
        """
        SELECT coin_id, coin_value, coin_category, is_active
        FROM coins
        WHERE coin_tag_id = ?
        """,
        (tag_id,),
    )
    coin = cursor_db.fetchone()

    if coin:
        coin_id, coin_value, category_id, is_active = coin

        # Lookup category name
        cursor_db.execute(
            """
            SELECT coin_category_name
            FROM coin_category
            WHERE coin_category_id = ?
            """,
            (category_id,),
        )
        category = cursor_db.fetchone()
        category_name = category[0] if category else "no_category"

        connection_db.close()
        return jsonify(
            {
                "id": coin_id,
                "type": "coin",
                "user_name": None,
                "remaining_time": None,
                "user_acro": None,
                "coin_value": coin_value,
                "active": is_active,
                "coin_category_name": category_name,
            }
        )

    connection_db.close()
    return jsonify({"error": "No matching user or coin found"}), 404


@bp_nodes.route("/get_identification", methods=["GET"])
def get_identification():
    user_tag_id = request.args.get("user_tag_id")

    if not user_tag_id:
        return jsonify({"error": "user_tag_id is required"}), 400

    connection_db = sqlite3.connect("database.db")
    cursor_db = connection_db.cursor()

    cursor_db.execute(
        "SELECT user_name, user_time_offset, user_game_start_timestamp FROM users WHERE user_tag_id = ?",
        (user_tag_id,),
    )
    user = cursor_db.fetchone()

    connection_db.close()

    if user:
        name, offset, start_str = user
        time = count_remaining_time(start_str, offset)
        return jsonify({"name": name, "user_time": time})
    return jsonify({"error": "User not found"}), 404


@bp_nodes.route("/subtract_time", methods=["GET"])
def substract_time():
    time_to_subtract = request.args.get("time_to_subtract")
    user_tag_id = request.args.get("user_tag_id")

    if not time_to_subtract or not user_tag_id:
        return jsonify({"error": "time_to_substract and user_tag_id are required"}), 404

    return addition_of_time(user_tag_id, time_to_subtract, "-")


@bp_nodes.route("/add_time", methods=["GET"])
def add_time():
    time_to_add = request.args.get("time_to_add")
    user_tag_id = request.args.get("user_tag_id")

    if not time_to_add or not user_tag_id:
        return jsonify({"error": "time_to_add and user_tag_id are required"}), 404

    return addition_of_time(user_tag_id, time_to_add, "+")


@bp_nodes.route("/change_time", methods=["GET"])
def change_time():
    time_to_add = request.args.get("input_time")
    user_tag_id = request.args.get("user_tag_id")

    if not time_to_add or not user_tag_id:
        return jsonify({"error": "input_time and user_tag_id are required"}), 404

    symbol = "+"
    if not time_to_add[-1].isdecimal():
        symbol = time_to_add[-1]
        if symbol not in config.ALLOWED_OPERATORS:
            return jsonify({"error": "time must be integer"}), 404
        else:
            time_to_add = time_to_add[:-1]

    return addition_of_time(user_tag_id, time_to_add, symbol)


@bp_nodes.route("/add_coinval", methods=["GET"])
def add_coinval():
    coin_tag_id = request.args.get("coin_tag_id")
    user_tag_id = request.args.get("user_tag_id")
    if not coin_tag_id or not user_tag_id:
        return jsonify({"error": "coin_tag_id and user_tag_id are required"}), 400

    if is_user_tag(coin_tag_id):
        return jsonify({"error": "Provided tag belongs to a user, not a coin"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute(
        "SELECT user_time_offset, user_game_start_timestamp FROM users WHERE user_tag_id = ?",
        (user_tag_id,),
    )
    user = cursor_db.fetchone()

    cursor_db.execute(
        "SELECT coin_value, is_active FROM coins WHERE coin_tag_id = ?", (coin_tag_id,)
    )
    coin = cursor_db.fetchone()

    if user and coin:
        if len(coin) < 2:
            connection_db.close()
            return jsonify({"error": "problem, noooo"}), 404
        if coin[1] == 0:
            connection_db.close()
            return jsonify({"error": "coin is inactive"}), 404
        new_offset = coin[0] + user[0]
        cursor_db.execute(
            "UPDATE users SET user_time_offset = ? WHERE user_tag_id = ?",
            (new_offset, user_tag_id),
        )

        cursor_db.execute(
            "UPDATE coins SET last_used = DATETIME('NOW'), is_active = ? WHERE coin_tag_id = ?",
            (0, coin_tag_id),
        )

        connection_db.commit()
        connection_db.close()

        time = count_remaining_time(user[1], new_offset)
        return jsonify({"status": "success", "user_time": time})

    else:
        connection_db.close()
        return jsonify({"error": "User or tag found"}), 404


@bp_nodes.route("/set_coinval", methods=["GET"])
def set_coinval():
    coin_tag_id = request.args.get("coin_tag_id")
    coin_value = request.args.get("coin_value")
    if not coin_tag_id or not coin_value:
        return jsonify({"error": "coin_tag_id is required"}), 400

    if is_user_tag(coin_tag_id):
        return jsonify({"error": "Provided tag belongs to a user, not a coin"}), 400

    try:
        coin_value = int(coin_value)
    except:
        return jsonify({"error": "coin_value must be integer"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute(
        "SELECT coin_tag_id FROM coins WHERE coin_tag_id = ?", (coin_tag_id,)
    )
    coin = cursor_db.fetchone()
    if coin is not None:  # coin_tag_id is already in database
        cursor_db.execute(
            "UPDATE coins SET coin_value = ? WHERE coin_tag_id = ?",
            (coin_value, coin_tag_id),
        )
    else:
        insert_coin(cursor_db, coin_tag_id, coin_value, 0)

    connection_db.commit()
    connection_db.close()

    return jsonify({"status": "success"})


@bp_nodes.route("/activate_coin", methods=["GET"])
def activate_coin():
    coin_tag_id = request.args.get("coin_tag_id")

    if coin_tag_id is None:
        return jsonify({"error": "coin tag is required"})

    if is_user_tag(coin_tag_id):
        return jsonify({"error": "Provided tag belongs to a user, not a coin"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()
    cursor_db.execute(
        "SELECT coin_tag_id FROM coins WHERE coin_tag_id = ?", (coin_tag_id,)
    )
    coin = cursor_db.fetchone()
    if coin is None:
        insert_coin(cursor_db, coin_tag_id, 0, 0)

    cursor_db.execute(
        "UPDATE coins SET is_active = 1 WHERE coin_tag_id = ?", (coin_tag_id,)
    )

    connection_db.commit()
    connection_db.close()

    return jsonify({"status": "success"})


@bp_nodes.route("/init_user_tag", methods=["GET"])
def init_user_tag():
    user_tag_id = request.args.get("user_tag_id")

    if not user_tag_id:
        return jsonify({"error": "no user_tag_id"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT user_id FROM users WHERE user_tag_id = ?", (user_tag_id,))
    user = cursor_db.fetchone()

    response = {}

    if user:
        response["status"] = "error"
        response["text"] = "user already exist"
    else:
        response["status"] = "success"
        insert_user(cursor_db, user_tag_id, "initname", "x", 0, datetime.now(), 0)

    connection_db.commit()
    connection_db.close()

    return jsonify(response)
