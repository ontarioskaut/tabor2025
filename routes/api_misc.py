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
