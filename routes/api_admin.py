import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, request

import config
from db.helpers import insert_coin, insert_user
from utils.time_utils import count_new_offset, count_remaining_time, count_new_time

bp_admin = Blueprint("admin", __name__)


@bp_admin.route("/set_user_field", methods=["GET"])
def set_user_field():
    user_id = request.args.get("user_id")
    field_name = request.args.get("field_name")
    new_value = request.args.get("new_value")

    if not user_id or not field_name or not new_value:
        return (
            jsonify(
                {
                    "error": "wrong arguments input should be user_id, filed_name, new_value"
                }
            ),
            400,
        )

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        query = f"UPDATE users SET {field_name} = ? WHERE user_id = ?"
        cursor_db.execute(query, (new_value, user_id))
        connection_db.commit()

        if cursor_db.rowcount == 0:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "No user found with the given user_id",
                    }
                ),
                404,
            )
        return jsonify({"status": "success"})

    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection_db.close()


# ------------------------------------------------------------------------------
#
# ------------------html--------------------------------------------------------
#
# ------------------------------------------------------------------------------


# -----------------------------users-------------------------------------------


@bp_admin.route("/update_user", methods=["POST"])
def update_user():
    user_id = request.form.get("user_id")
    user_tag_id = request.form.get("user_tag_id")
    user_name = request.form.get("user_name")
    user_acro = request.form.get("user_acro")
    user_time_offset = request.form.get("user_time_offset")
    user_game_start_timestamp = request.form.get("user_game_start_timestamp")
    is_displayed = request.form.get("is_displayed")  # returns string "on" or None
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all(
        [user_tag_id, user_name, user_acro, user_time_offset, user_game_start_timestamp]
    ):
        return jsonify({"error": "All fields are required."}), 400

    if is_displayed is None:
        is_displayed_res = 0
    else:
        is_displayed_res = 1

    tags = cursor_db.execute(
        "SELECT user_id, user_name FROM users WHERE user_tag_id = ?", (user_tag_id,)
    ).fetchone()
    if tags is not None and tags[0] != int(user_id):
        connection_db.close()
        return (
            jsonify(
                {"error": f"user tag is already in use, by user: {tags[0]}, {tags[1]}"}
            ),
            400,
        )

    if not user_time_offset.isnumeric():
        return jsonify({"error": "offset must me integers"})

    try:
        cursor_db.execute(
            """
            UPDATE users
            SET user_tag_id = ?, user_name = ?, user_acro = ?, user_time_offset = ?, user_game_start_timestamp = ?, is_displayed = ?
            WHERE user_id = ?
        """,
            (
                user_tag_id,
                user_name,
                user_acro,
                user_time_offset,
                user_game_start_timestamp,
                is_displayed_res,
                user_id,
            ),
        )

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@bp_admin.route("/add_user", methods=["POST"])
def add_user():
    user_tag_id = request.form.get("user_tag_id")
    user_name = request.form.get("user_name")
    user_acro = request.form.get("user_acro")
    user_time_offset = request.form.get("user_time_offset")
    user_game_start_timestamp = request.form.get("user_game_start_timestamp")
    is_displayed = request.form.get("is_displayed")  # returns string "on" or None

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all(
        [user_tag_id, user_name, user_acro, user_time_offset, user_game_start_timestamp]
    ):
        return jsonify({"error": "All fields are required."}), 400

    if is_displayed is None:
        is_displayed_res = 0
    else:
        is_displayed_res = 1

    tags = cursor_db.execute(
        "SELECT user_id, user_name FROM users WHERE user_tag_id = ?", (user_tag_id,)
    ).fetchone()
    if tags is not None:
        connection_db.close()
        return (
            jsonify(
                {"error": f"user tag is already in use, by user: {tags[0]}, {tags[1]}"}
            ),
            400,
        )

    if not user_time_offset.isdecimal():
        return jsonify({"error": "offset must me integers"})

    try:
        insert_user(
            cursor_db,
            user_tag_id,
            user_name,
            user_acro,
            user_time_offset,
            user_game_start_timestamp,
            is_displayed_res,
        )
        connection_db.commit()
    except sqlite3.Error as e:
        connection_db.close()
        return jsonify({"error": f"An error occurred during inserting: {e}"}), 400
    finally:
        connection_db.close()

    return jsonify({"status": "succes"})


@bp_admin.route("/delete_user", methods=["POST"])
def delete_user():
    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


@bp_admin.route("/bulk_add_user_time", methods=["POST"])
def bulk_add_user_time():
    data = request.get_json()
    user_ids = data.get("user_ids")
    time_offset = data.get("time_offset")

    if not user_ids or not time_offset:
        return jsonify({"error": "user_ids and time_offset are required"}), 400

    symbol = "+"
    if not time_offset[-1].isdecimal():
        symbol = time_offset[-1]
        if symbol not in config.ALLOWED_OPERATORS:
            return jsonify({"error": "time_offset must be an integer"}), 400
        time_offset = time_offset[:-1]

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for user_id in user_ids:
            cursor_db.execute(
                "SELECT user_time_offset, user_game_start_timestamp FROM users WHERE user_id = ?", (user_id,)
            )
            user = cursor_db.fetchone()

            if user:
                current_offset, start = user

                new_time = count_new_time(current_offset, start, time_offset, symbol)
                cursor_db.execute(
                    "UPDATE users SET user_time_offset = ? WHERE user_id = ?",
                    (new_time, user_id),
                )

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


# --------------------------- coins -------------------------------------------


@bp_admin.route("/update_coin", methods=["POST"])
def update_coin():
    elem_id = request.form.get("coin_id")
    elem_tag_id = request.form.get("coin_tag_id")
    elem_value = request.form.get("coin_value")
    elem_category = request.form.get("coin_category")
    elem_last_used = request.form.get("last_used")
    elem_is_active = request.form.get("is_active")

    if elem_is_active is None:
        elem_is_active_int = 0
    else:
        elem_is_active_int = 1

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_tag_id, elem_value, elem_category, elem_last_used]):
        return jsonify({"error": "All fields are required."}), 400

    tags = cursor_db.execute(
        "SELECT coin_id FROM coins WHERE coin_tag_id = ?", (elem_tag_id,)
    ).fetchone()
    if tags is not None and tags[0] != int(elem_id):
        connection_db.close()
        return jsonify({"error": f"coin tag is already in use, by : {tags[0]}"}), 400

    if not elem_category.isnumeric() or not elem_value.isnumeric():
        return jsonify({"error": "category and offset must me integers"})

    try:
        cursor_db.execute(
            """
            UPDATE coins
            SET coin_tag_id = ?, coin_value = ?, coin_category = ?, last_used = ?, is_active = ?
            WHERE coin_id = ?
        """,
            (
                elem_tag_id,
                elem_value,
                elem_category,
                elem_last_used,
                elem_is_active_int,
                elem_id,
            ),
        )

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@bp_admin.route("/add_coin", methods=["POST"])
def add_coin():
    elem_tag_id = request.form.get("coin_tag_id")
    elem_value = request.form.get("coin_value")
    elem_category = request.form.get("coin_category")
    elem_last_used = request.form.get("last_used")
    elem_activity = request.form.get("is_active")

    if elem_activity is None:
        elem_activity_int = 0
    else:
        elem_activity_int = 1

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_tag_id, elem_value, elem_category, elem_last_used]):
        return jsonify({"error": "All fields are required."}), 400

    tags = cursor_db.execute(
        "SELECT coin_id FROM coins WHERE coin_tag_id = ?", (elem_tag_id,)
    ).fetchone()
    if tags is not None:
        connection_db.close()
        return jsonify({"error": f"coin tag is already in use, by: {tags[0]}"}), 400

    if not elem_category.isnumeric() or not elem_value.isnumeric():
        return jsonify({"error": "category and value must me integers"})

    try:
        insert_coin(
            cursor_db,
            elem_tag_id,
            elem_value,
            elem_category,
            elem_last_used,
            elem_activity_int,
        )
        connection_db.commit()
    except sqlite3.Error as e:
        connection_db.close()
        return jsonify({"error": f"An error occurred during inserting: {e}"}), 400
    finally:
        connection_db.close()

    return jsonify({"status": "succes"})


@bp_admin.route("/delete_coin", methods=["POST"])
def delete_coin():
    elem_id = request.form.get("coin_id")
    if not elem_id:
        return jsonify({"error": "coin_id is required"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM coins WHERE coin_id = ?", (elem_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


@bp_admin.route("/bulk_set_coin_field", methods=["POST"])
def bulk_set_coin_field():
    data = request.get_json()
    coin_ids = data.get("coin_ids")
    field_name = data.get("field_name")
    new_value = data.get("new_value")

    if not coin_ids or not field_name or not new_value:
        return (
            jsonify({"error": "coin_ids, field_name, and new_value are required"}),
            400,
        )

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for coin_id in coin_ids:
            query = f"UPDATE coins SET {field_name} = ? WHERE coin_id = ?"
            cursor_db.execute(query, (new_value, coin_id))

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


@bp_admin.route("/bulk_add_coin_time", methods=["POST"])
def bulk_add_coin_time():
    data = request.get_json()
    elem_ids = data.get("coin_ids")
    time_offset = data.get("time_offset")

    if not elem_ids or not time_offset:
        return jsonify({"error": "elem_ids and time_offset are required"}), 400

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            cursor_db.execute(
                "SELECT coin_value FROM coins WHERE coin_id = ?", (elem_id,)
            )
            elem = cursor_db.fetchone()

            if elem:
                current_offset = elem[0]
                new_offset = current_offset + time_offset
                cursor_db.execute(
                    "UPDATE coins SET coin_value = ? WHERE coin_id = ?",
                    (new_offset, elem_id),
                )

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


# ---------------------------users categories ---------------------------------


@bp_admin.route("/update_user_category", methods=["POST"])
def update_user_category():
    elem_id = request.form.get("category_id")
    elem_name = request.form.get("category_name")

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_name]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute(
            """
            UPDATE users_category
            SET user_category_name = ?
            WHERE user_category_id = ?
        """,
            (elem_name, elem_id),
        )

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@bp_admin.route("/add_user_category", methods=["POST"])
def add_user_category():
    elem_name = request.form.get("category_name")

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not elem_name:
        return jsonify({"error": "Name is required."}), 400

    try:
        cursor_db.execute(f"SELECT MAX(user_category_id) FROM users_category")
        new_id = cursor_db.fetchone()[0]
        new_id = new_id + 1 if new_id is not None else 1
        temp = f"{new_id}, '{elem_name}'"
        cursor_db.execute("Insert INTO users_category VALUES (" + temp + ")")
        connection_db.commit()
    except sqlite3.Error as e:
        connection_db.close()
        return jsonify({"error": f"An error occurred during inserting: {e}"}), 400
    finally:
        connection_db.close()

    return jsonify({"status": "succes"})


@bp_admin.route("/delete_user_category", methods=["POST"])
def delete_user_category():
    elem_id = request.form.get("category_id")
    if not elem_id:
        return jsonify({"error": "id is required"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute(
            "DELETE FROM users_category WHERE user_category_id = ?", (elem_id,)
        )
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


@bp_admin.route("/bulk_add_user_time_category", methods=["POST"])
def bulk_add_user_time_category():
    data = request.get_json()
    elem_ids = data.get("ids")
    time_offset = data.get("time_offset")

    if not elem_ids or not time_offset:
        return jsonify({"error": "elem_ids and time_offset are required"}), 400

    symbol = "+"
    if not time_offset[-1].isdecimal():
        symbol = time_offset[-1]
        print(symbol)
        if symbol not in config.ALLOWED_OPERATORS:
            return jsonify({"error": "time_offset must be an integer"}), 400
        time_offset = time_offset[:-1]

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            cursor_db.execute(
                """SELECT users.user_id, user_time_offset 
                              FROM users JOIN categories_rel ON users.user_id = categories_rel.user_id
                              WHERE categories_rel.category_id = ?""",
                (elem_id,),
            )
            elems = cursor_db.fetchall()

            for elem in elems:
                current_offset = elem[1]
                # new_offset = current_offset + time_offset
                new_offset = count_new_offset(current_offset, time_offset, symbol)
                cursor_db.execute(
                    """UPDATE users 
                                  SET user_time_offset = ? 
                                  WHERE user_id = ?""",
                    (new_offset, elem[0]),
                )

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


# -------------------- users category relations--------------------------------


@bp_admin.route("/add_user_cat_rel", methods=["POST"])
def add_user_cat_rel():
    user_id_str = request.form.get("user_id")
    cat_id_str = request.form.get("category_id")

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([user_id_str, cat_id_str]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute(
            """
            INSERT INTO categories_rel (user_id, category_id)
                    VALUES (?, ?)
        """,
            (int(user_id_str), int(cat_id_str)),
        )

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@bp_admin.route("/update_user_cat_rel", methods=["POST"])
def update_user_cat_rel():
    row_id = request.form.get("row_id")
    user_id_str = request.form.get("user_id")
    cat_id_str = request.form.get("category_id")

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([user_id_str, cat_id_str]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute(
            """
            UPDATE categories_rel
            SET user_id = ?, category_id = ?
            WHERE id = ?
        """,
            (int(user_id_str), int(cat_id_str), int(row_id)),
        )

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@bp_admin.route("/delete_user_cat_rel", methods=["POST"])
def delete_user_cat_rel():
    elem_id = request.form.get("row_id")
    if not elem_id:
        return jsonify({"error": "id is required"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM categories_rel WHERE id = ?", (elem_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


# ---------------------- user categories relation second try ------------------


@bp_admin.route("/toggle_user_cat_rel", methods=["POST"])
def toggle_user_cat_rel():
    user_id = request.form.get("user_id")
    category_id = request.form.get("category_id")
    is_checked = request.form.get("is_checked") == "on"

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if is_checked:
        cursor_db.execute(
            "INSERT INTO categories_rel (user_id, category_id) VALUES (?, ?)",
            (user_id, category_id),
        )
    else:
        cursor_db.execute(
            "DELETE FROM categories_rel WHERE user_id = ? AND category_id = ?",
            (user_id, category_id),
        )

    connection_db.commit()
    connection_db.close()

    return jsonify({"message": "Operation successful!"})


# --------------------------------------- coin categories----------------------


@bp_admin.route("/update_coin_category", methods=["POST"])
def update_coin_category():
    elem_id = request.form.get("category_id")
    elem_name = request.form.get("category_name")

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_name]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute(
            """
            UPDATE coin_category
            SET coin_category_name = ?
            WHERE coin_category_id = ?
        """,
            (elem_name, elem_id),
        )

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@bp_admin.route("/add_coin_category", methods=["POST"])
def add_coin_category():
    elem_name = request.form.get("category_name")

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not elem_name:
        return jsonify({"error": "Name is required."}), 400

    try:
        cursor_db.execute(f"SELECT MAX(coin_category_id) FROM coin_category")
        new_id = cursor_db.fetchone()[0]
        new_id = new_id + 1 if new_id is not None else 1
        temp = f"{new_id}, '{elem_name}'"
        cursor_db.execute("Insert INTO coin_category VALUES (" + temp + ")")
        connection_db.commit()
    except sqlite3.Error as e:
        connection_db.close()
        return jsonify({"error": f"An error occurred during inserting: {e}"}), 400
    finally:
        connection_db.close()

    return jsonify({"status": "succes"})


@bp_admin.route("/delete_coin_category", methods=["POST"])
def delete_coin_category():
    elem_id = request.form.get("category_id")
    if not elem_id:
        return jsonify({"error": "id is required"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute(
            "DELETE FROM coin_category WHERE coin_category_id = ?", (elem_id,)
        )
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


@bp_admin.route("/bulk_add_coin_time_category", methods=["POST"])
def bulk_add_coin_time_category():
    data = request.get_json()
    elem_ids = data.get("ids")
    time_offset = data.get("time_offset")

    if not elem_ids or not time_offset:
        return jsonify({"error": "elem_ids and time_offset are required"}), 400

    symbol = "+"
    if not time_offset[-1].isdecimal():
        symbol = time_offset[-1]
        if symbol not in config.ALLOWED_OPERATORS:
            return jsonify({"error": "time_offset must be an integer"}), 400
        time_offset = time_offset[:-1]

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            cursor_db.execute(
                "SELECT coin_id, coin_value FROM coins WHERE coin_category = ?",
                (elem_id,),
            )
            elems = cursor_db.fetchall()

            for elem in elems:
                current_offset = elem[1]
                new_offset = count_new_offset(current_offset, time_offset, symbol)
                cursor_db.execute(
                    "UPDATE coins SET coin_value = ? WHERE coin_id = ?",
                    (new_offset, elem[0]),
                )

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()

