import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

import config
from db.helpers import insert_coin, insert_user
from utils.time_utils import *

bp_admin_pages = Blueprint("admin_pages", __name__)


@bp_admin_pages.route("/")
def dashboard():
    return render_template("admin_index.html")


@bp_admin_pages.route("/users", methods=["GET"])
def admin_users():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute("SELECT * FROM users").fetchall()
    # rows = cursor_db.execute("""SELECT user_id, user_tag_id, user_name, users.user_acro, users_category.user_category_name, users.user_time_offset, users.user_game_start_timestamp, users.is_displayed
    #     FROM users
    # """).fetchall()

    connection_db.close()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )  # Format the current time as a string

    user_rows = [dict(row) for row in rows]

    for user in user_rows:
        raw_time = user["user_game_start_timestamp"]
        if raw_time:
            try:
                dt = datetime.fromisoformat(raw_time)
                user["user_game_start_timestamp"] = dt.replace(microsecond=0).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except Exception as e:
                print(f"Error parsing timestamp: {raw_time} -> {e}")

    return render_template(
        "admin_users_tmp.html", users=user_rows, current_time=current_time
    )


@bp_admin_pages.route("/coins", methods=["GET"])
def admin_coins():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()
    # rows = cursor_db.execute('SELECT * FROM (coins JOIN coin_category ON coins.coin_category = coin_category.coin_category_id) ').fetchall()
    rows = cursor_db.execute(
        """SELECT coins.coin_id, coins.coin_tag_id, coins.coin_value, coins.last_used, coins.is_active,
       coin_category.coin_category_id, coin_category.coin_category_name
        FROM coins
        JOIN coin_category ON coins.coin_category = coin_category.coin_category_id
    """
    ).fetchall()

    connection_db.close()

    return render_template("admin_coins_tmp.html", coins=rows)


@bp_admin_pages.route("/categories_user", methods=["GET"])
def admin_user_categories():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute("SELECT * FROM users_category").fetchall()

    connection_db.close()

    return render_template("admin_cat_users_tmp.html", categories=rows)


@bp_admin_pages.route("/user_cat_relation", methods=["GET"])
def admin_user_cat_relation():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute(
        """SELECT categories_rel.id, categories_rel.user_id, users.user_name,
                                        categories_rel.category_id, users_category.user_category_name
                                    FROM categories_rel
                                        JOIN users ON users.user_id = categories_rel.user_id
                                        JOIN users_category ON users_category.user_category_id = categories_rel.category_id;
                             """
    ).fetchall()

    connection_db.close()

    return render_template("admin_cat_rel_tmp.html", input_data=rows)


@bp_admin_pages.route("/user_cat_relation_v02", methods=["GET"])
def admin_user_cat_relation_v02():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    users_rows = cursor_db.execute(
        """SELECT user_id, user_name FROM users"""
    ).fetchall()
    categories_rows = cursor_db.execute(
        """SELECT user_category_id, user_category_name FROM users_category"""
    ).fetchall()
    rel_rows = cursor_db.execute("""SELECT * FROM categories_rel""").fetchall()

    connection_db.close()

    return render_template(
        "admin_cat_rel_tmp_v02.html",
        users=users_rows,
        categories=categories_rows,
        relation=rel_rows,
    )


# almost identical to users category
@bp_admin_pages.route("/categories_coin", methods=["GET"])
def admin_coin_categories():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute("SELECT * FROM coin_category").fetchall()

    connection_db.close()

    return render_template("admin_cat_coin_tmp.html", categories=rows)


@bp_admin_pages.route("/show_times", methods=["GET"])
def show_times():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute(
        """SELECT user_name, user_time_offset, user_game_start_timestamp FROM users """
    ).fetchall()
    connection_db.close()

    result = []

    for name, offset, start in rows:
        time_int = (
            offset - (datetime.now() - datetime.fromisoformat(start)).total_seconds()
        )
        temp_dict = {}
        temp_dict["name"] = name
        temp_dict["time"] = seconds_to_text(time_int)
        result.append(temp_dict)

    return render_template("times_tiles_tmp.html", users=result)


@bp_admin_pages.route("/show_times_02", methods=["GET"])
def show_times_02():
    return render_template("times_tiles_v02.html", config=config)


@bp_admin_pages.route("/show_logs", methods=["GET"])
def show_logs():
    user = request.args.get("user_id")

    if user and not user.isnumeric():
        return jsonify({"status": "error", "message": "wrong user id"}), 500

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    if user is None or user == "":
        rows = cursor_db.execute(
            "SELECT * FROM (logs JOIN users ON logs.user_id = users.user_id) ORDER BY id DESC"
        ).fetchall()
    else:
        rows = cursor_db.execute(
            "SELECT * FROM (logs JOIN users ON logs.user_id = users.user_id) WHERE logs.user_id = ? ORDER BY id DESC",
            (user,),
        ).fetchall()

    connection_db.close()

    return render_template("logs_tmp.html", logs=rows)

