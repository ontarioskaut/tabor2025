import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, request

import config
from db.helpers import insert_coin, insert_user

bp_misc = Blueprint("misc", __name__)


@bp_misc.route("/get_logs", methods=["GET"])
def show_logs_json():
    connection_db = sqlite3.connect(config.DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute("""SELECT * FROM logs """)
    result = cursor_db.fetchall()

    connection_db.close()

    return result


@bp_misc.route("/get_active", methods=["GET"])
def get_active():
    return str(getattr(config, "SYSTEM_ACTIVE", True))


@bp_misc.route("/set_active", methods=["POST"])
def set_active():
    new_state = request.form.get("state")
    print("Changing state:", new_state)
    if new_state == "True":
        config.SYSTEM_ACTIVE = True
    else:
        config.SYSTEM_ACTIVE = False
    return "True"


@bp_misc.route("/get_allocated_time", methods=["GET"])
def get_allocated_time():
    return str(getattr(config, "ALLOCATED_TIME", 0))
