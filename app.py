#!/usr/bin/env python3
# import json
from flask import (Flask, jsonify, request, render_template,
                   render_template_string)
import sqlite3
from datetime import datetime


DATABASE_NAME = "database.db"
ALLOWED_OPERATORS = {'+', '-', '*', '%'}

# -----------------------------------------------------------------------------
#                            creation and definition of tables
# -----------------------------------------------------------------------------


def create_user_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_tag_id TEXT,
        user_name TEXT,
        user_acro TEXT,
        user_time_offset INTEGER,
        user_game_start_timestamp DATETIME,
        is_displayed BOOLEAN
    )
    """)


def create_category_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users_category (
        user_category_id INTEGER PRIMARY KEY,
        user_category_name TEXT
    )""")

    cur.execute("""
    INSERT OR IGNORE INTO
                users_category (user_category_id, user_category_name)
                VALUES (0, 'no_category')
    """)


def create_coins_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coins (
        coin_id INTEGER PRIMARY KEY,
        coin_tag_id TEXT,
        coin_value INTEGER,
        coin_category INTEGER,
        last_used DATETIME,
        is_active BOOLEAN
    )""")


def create_coin_category_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coin_category (
        coin_category_id INTEGER PRIMARY KEY,
        coin_category_name TEXT
    )""")
    cur.execute("""
        INSERT OR IGNORE INTO
                coin_category (coin_category_id, coin_category_name)
                VALUES (0, 'no_category')
    """)


def create_log_table(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME,
        user_id INTEGER,
        amount INTEGER,
        details TEXT
    )""")


def create_log_triggers(cur):
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS user_offset_update
        AFTER UPDATE
        ON users
        WHEN NEW.user_time_offset <> OLD.user_time_offset
    BEGIN
        INSERT INTO logs (timestamp, user_id, amount, details)
        VALUES (DATETIME('NOW'), NEW.user_id,
                NEW.user_time_offset - OLD.user_time_offset,
                'updated offset');
    END;
    """)


def create_categories_relation(cur):
    # one to many relation
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories_rel (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        category_id INTEGER
    )""")


def create_tables(name: str):
    connection_db = sqlite3.connect(name)
    cursor_db = connection_db.cursor()
    create_user_db(cursor_db)
    create_coins_db(cursor_db)
    create_category_db(cursor_db)
    create_coin_category_db(cursor_db)

    create_categories_relation(cursor_db)

    create_log_table(cursor_db)
    create_log_triggers(cursor_db)

    connection_db.commit()
    cursor_db.close()

# -----------------------------------------------------------------------------
# ------------------------------- aux functions -------------------------------
# -----------------------------------------------------------------------------


def insert_user(cur, tag_id: str, name: str, acro: str,
                offset: int, start: int, is_displayed: int):
    cur.execute(f"SELECT MAX(user_id) FROM users")
    new_id = cur.fetchone()[0]
    new_id = new_id + 1 if new_id is not None else 1
    temp = f"{new_id}, '{tag_id}', '{name}', '{acro}', {offset}, '{start}', {is_displayed}"
    cur.execute("Insert INTO users VALUES (" + temp + ")")

def insert_coin(cur, tag_id: str, value: int, category: int,
                last_used:str = '1970-01-01 00:00:00', is_active: int = 0):
    # last two argumemts are not required and automatically filled with "zero" value
    cur.execute(f"SELECT MAX(coin_id) FROM coins")
    new_id = cur.fetchone()[0]
    new_id = new_id + 1 if new_id is not None else 1
    temp = f"{new_id}, '{tag_id}', {value}, {category}, '{last_used}', {is_active}"
    cur.execute("Insert INTO coins VALUES (" + temp + ")")


def seconds_to_text(total_seconds: int):
    is_negative = total_seconds < 0
    abs_seconds = abs(total_seconds)

    hours = abs_seconds // 3600
    minutes = (abs_seconds % 3600) // 60
    seconds = abs_seconds % 60

    # Format to HH:MM:SS
    formatted_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    if is_negative:
        return f"-{formatted_time}"
    return formatted_time


def count_remaining_time(timestamp: str, offset: int):
    start_int = datetime.fromisoformat(timestamp)
    time_diff = (datetime.now() - start_int).total_seconds()
    return offset - round(time_diff)


def count_new_offset(old_offset: int, input: int, mode: str):
        if mode == '+':
            new_offset = old_offset + input
        elif mode == '-':
            new_offset = old_offset - input
        elif mode == '*':
            new_offset = old_offset * input
        elif mode == '%':
            new_offset = old_offset * ((100 + input) / 100)
        return new_offset


def test_show_users(cur):
    test = cur.execute("SELECT * from users")
    print(test.fetchall())


# -----------------------------------------------------------------------------
# --------------FLASK-------------------------------------------
# -----------------------------------------------------------------------------
app = Flask(__name__, static_url_path='/static', static_folder='static')
@app.route('/')
def index():
    return "hello world <img src='/static/others/pic01.png'>"


# -----------------------------------------------------------------------------
# ------------------API FOR NODES------------------------------
# -----------------------------------------------------------------------------
@app.route('/get_identification', methods=['GET'])
def get_identification():
    user_tag_id = request.args.get('user_tag_id')

    if not user_tag_id:
        return jsonify({"error": "user_tag_id is required"}), 400

    connection_db = sqlite3.connect("database.db")
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT user_name, user_time_offset, user_game_start_timestamp FROM users WHERE user_tag_id = ?", (user_tag_id,))
    user = cursor_db.fetchone()

    connection_db.close()

    if user:
        name, offset, start_str = user
        time = count_remaining_time(start_str, offset)
        return jsonify({"name":name, "user_time": time})
    return jsonify({"error": "User not found"}), 404


def addition_of_time(user_tag_id, time_to_change, mode: str = '+'):
    if not time_to_change or not user_tag_id:
        return jsonify({"error": "time_to_subtract and user_tag_id are required"}), 400

    try:
        time_to_change = int(time_to_change)
    except ValueError:
        return jsonify({"error": "time must be an integer"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT user_time_offset, user_game_start_timestamp FROM users WHERE user_tag_id = ?", (user_tag_id,))
    user = cursor_db.fetchone()

    if user:
        current_offset, start_time = user
        print(user)
        new_offset = count_new_offset(current_offset, time_to_change, mode)
        cursor_db.execute("UPDATE users SET user_time_offset = ? WHERE user_tag_id = ?", (new_offset, user_tag_id))
        connection_db.commit()
        connection_db.close()

        time = count_remaining_time(start_time, new_offset)
        return jsonify({"status": "success", "user_time": time})
    else:
        connection_db.close()
        return jsonify({"error": "User not found"}), 404


@app.route('/subtract_time', methods=['GET'])
def substract_time():
    time_to_subtract = request.args.get('time_to_subtract')
    user_tag_id = request.args.get('user_tag_id')

    if not time_to_subtract or not user_tag_id:
        return jsonify({"error": "time_to_substract and user_tag_id are required"}), 404

    return addition_of_time(user_tag_id, time_to_subtract, '-')


@app.route('/add_time', methods=['GET'])
def add_time():
    time_to_add = request.args.get('time_to_add')
    user_tag_id = request.args.get('user_tag_id')

    if not time_to_add or not user_tag_id:
        return jsonify({"error": "time_to_add and user_tag_id are required"}), 404

    return addition_of_time(user_tag_id, time_to_add, '+')

@app.route('/change_time', methods=['GET'])
def change_time():
    time_to_add = request.args.get('input_time')
    user_tag_id = request.args.get('user_tag_id')

    if not time_to_add or not user_tag_id:
        return jsonify({"error": "input_time and user_tag_id are required"}), 404

    symbol = '+'
    if not time_to_add[-1].isdecimal():
        symbol = time_to_add[-1]
        if symbol not in ALLOWED_OPERATORS:
            return jsonify({"error": "time must be integer"}), 404
        else:
            time_to_add = time_to_add[:-1]


    return addition_of_time(user_tag_id, time_to_add, symbol)


@app.route('/add_coinval', methods=['GET'])
def add_coinval():
    # it would be prettier to use "addition of time" again, but this way, i don't have to open database two times
    coin_tag_id = request.args.get('coin_tag_id')
    user_tag_id = request.args.get('user_tag_id')
    if not coin_tag_id or not user_tag_id:
        return jsonify({"error": "coin_tag_id and user_tag_id are required"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT user_time_offset, user_game_start_timestamp FROM users WHERE user_tag_id = ?", (user_tag_id,))
    user = cursor_db.fetchone()

    cursor_db.execute("SELECT coin_value, is_active FROM coins WHERE coin_tag_id = ?", (coin_tag_id,))
    coin = cursor_db.fetchone()


    if user and coin:
        if len(coin) < 2:
            connection_db.close()
            return jsonify({"error": "problem, noooo"}), 404
        if coin[1] == 0:
            connection_db.close()
            return jsonify({"error": "coin is inactive"}), 404
        new_offset = coin[0] + user[0]
        cursor_db.execute("UPDATE users SET user_time_offset = ? WHERE user_tag_id = ?", (new_offset, user_tag_id))
        
        cursor_db.execute("UPDATE coins SET last_used = DATETIME('NOW'), is_active = ? WHERE coin_tag_id = ?", (0, coin_tag_id))

        connection_db.commit()
        connection_db.close()

        time = count_remaining_time(user[1], new_offset)
        return jsonify({"status": "success", "user_time": time})

    else:
        connection_db.close()
        return jsonify({"error": "User or tag found"}), 404


@app.route('/set_coinval', methods=['GET'])
def set_coinval():
    coin_tag_id = request.args.get('coin_tag_id')
    coin_value = request.args.get('coin_value')
    category = request.args.get('category')
    if not coin_tag_id or not coin_value or not category:
        return jsonify({"error": "coin_tag_id and coin_value and category are required"}), 400

    try:
        coin_value = int(coin_value)
        category = int(category)
    except:
        return jsonify({"error": "coin_value and category must be integers"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT coin_tag_id FROM coins WHERE coin_tag_id = ?", (coin_tag_id,))
    coin = cursor_db.fetchone()
    if coin is not None: # coin_tag_id is already in database
        cursor_db.execute("UPDATE coins SET coin_value = ?, coin_category = ? WHERE coin_tag_id = ?", (coin_value, category, coin_tag_id))
    else:
        insert_coin(cursor_db, coin_tag_id, coin_value, category)
    
    connection_db.commit()
    connection_db.close()

    return jsonify({"status": "success"})


@app.route('/activate_coin', methods=['GET'])
def activate_coin():
    coin_tag_id = request.args.get('coin_tag_id')

    if coin_tag_id is None:
        return jsonify({"error": "coin tag is required"})

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()
    cursor_db.execute("SELECT coin_tag_id FROM coins WHERE coin_tag_id = ?", (coin_tag_id,))
    coin = cursor_db.fetchone()
    if coin is None:
        insert_coin(cursor_db, coin_tag_id, 0, 0)
    
    cursor_db.execute("UPDATE coins SET is_active = 1 WHERE coin_tag_id = ?", (coin_tag_id,))

    connection_db.commit()
    connection_db.close()

    return jsonify({"status": "success"})


@app.route('/init_user_tag', methods=['GET'])
def init_user_tag():
    user_tag_id = request.args.get('user_tag_id')

    if not user_tag_id:
        return jsonify({"error": "no user_tag_id"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
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


#------------------------------------------------------------------------------
#-----------------------------Display api--------------
#------------------------------------------------------------------------------
@app.route('/get_time_simple', methods=['GET'])
def get_time_simple():
    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()
    cursor_db.execute("SELECT user_acro, user_time_offset, user_game_start_timestamp, is_displayed FROM users")
    rows = cursor_db.fetchall()
    connection_db.close()

    user_dict = {}

    for acro, offset, start, disp in rows:
        if int(disp) == 0:
            continue
        user_dict[acro] = count_remaining_time(start, offset)

    return jsonify(user_dict)

@app.route('/get_time', methods=['GET'])
# i thoght i will do something about this, but then i just left it so it's the same as simple version
def get_time():
    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()
    cursor_db.execute("SELECT user_acro, user_time_offset, user_game_start_timestamp, is_displayed FROM users")
    rows = cursor_db.fetchall()
    connection_db.close()

    user_dict = {}

    for acro, offset, start, disp in rows:
        if int(disp) == 0:
            continue

        user_dict[acro] = count_remaining_time(start, offset)

    return jsonify(user_dict)

#------------------------------------------------------------------------------
#-------------------------------Admin api-----------------------------------
#------------------------------------------------------------------------------
@app.route('/set_user_field', methods=['GET'])
def set_user_field():
    user_id = request.args.get('user_id')
    field_name = request.args.get('field_name')
    new_value = request.args.get('new_value')

    if not user_id or not field_name or not new_value:
        return jsonify({"error": "wrong arguments input should be user_id, filed_name, new_value"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        query = f"UPDATE users SET {field_name} = ? WHERE user_id = ?"
        cursor_db.execute(query, (new_value, user_id))
        connection_db.commit()

        if cursor_db.rowcount == 0:
            return jsonify({"status": "error", "message": "No user found with the given user_id"}), 404
        return jsonify({"status":"success"})

    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        connection_db.close()

#------------------------------------------------------------------------------
#
#------------------html--------------------------------------------------------
#
#------------------------------------------------------------------------------
@app.route('/admin')
def dashboard():
    # HTML for the dashboard with links
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Dashboard</title>
            <!-- Bootstrap CSS -->
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="mb-4 text-center">Welcome to the Admin Dashboard</h1>
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <ul class="list-group">
                            <li class="list-group-item"><a href="/admin/users" class="text-decoration-none">Users</a></li>
                            <li class="list-group-item"><a href="/admin/coins" class="text-decoration-none">Coins</a></li>
                            <li class="list-group-item"><a href="/admin/categories_user" class="text-decoration-none">User categories</a></li>
                            <li class="list-group-item"><a href="/admin/categories_coin" class="text-decoration-none">Coin categories</a></li>
                            <li class="list-group-item"><a href="/show_logs" class="text-decoration-none">Logs</a></li>
                            <li class="list-group-item"><a href="/show_times_02" class="text-decoration-none">Live timers</a></li>
                            <li class="list-group-item"><a href="/show_times" class="text-decoration-none">Current timers</a></li>
                            <li class="list-group-item"><a href="/admin/user_cat_relation_v02" class="text-decoration-none">User Category Relation v02</a></li>
                            <li class="list-group-item"><a href="/admin/user_cat_relation" class="text-decoration-none">User Category Relation</a></li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Bootstrap JS and dependencies -->
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        </body>
        </html>
    """
    return render_template_string(html)

# -----------------------------users-------------------------------------------

@app.route('/admin/users', methods=['GET'])
def admin_users():
    connection_db = sqlite3.connect(DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute('SELECT * FROM users').fetchall()
    #rows = cursor_db.execute("""SELECT user_id, user_tag_id, user_name, users.user_acro, users_category.user_category_name, users.user_time_offset, users.user_game_start_timestamp, users.is_displayed
    #     FROM users
    # """).fetchall()    
    
    connection_db.close()

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format the current time as a string

    user_rows = [dict(row) for row in rows]

    for user in user_rows:
        raw_time = user['user_game_start_timestamp']
        if raw_time:
            try:
                dt = datetime.fromisoformat(raw_time)
                user['user_game_start_timestamp'] = dt.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"Error parsing timestamp: {raw_time} -> {e}")

    return render_template('admin_users_tmp.html', users=user_rows, current_time=current_time)


@app.route('/admin/update_user', methods=['POST'])
def update_user():
    user_id = request.form.get('user_id')
    user_tag_id = request.form.get('user_tag_id')
    user_name = request.form.get('user_name')
    user_acro = request.form.get('user_acro')
    user_time_offset = request.form.get('user_time_offset')
    user_game_start_timestamp = request.form.get('user_game_start_timestamp')
    is_displayed = request.form.get('is_displayed') #returns string "on" or None
    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([user_tag_id, user_name, user_acro, user_time_offset, user_game_start_timestamp]):
        return jsonify({"error": "All fields are required."}), 400

    if is_displayed is None:
        is_displayed_res = 0
    else:
        is_displayed_res = 1

    tags = cursor_db.execute('SELECT user_id, user_name FROM users WHERE user_tag_id = ?', (user_tag_id,)).fetchone()
    if tags is not None and tags[0] != int(user_id):
        connection_db.close()
        return jsonify({"error":f"user tag is already in use, by user: {tags[0]}, {tags[1]}"}), 400

    if  not user_time_offset.isnumeric():
        return jsonify({"error":"offset must me integers"})

    try:
        cursor_db.execute("""
            UPDATE users
            SET user_tag_id = ?, user_name = ?, user_acro = ?, user_time_offset = ?, user_game_start_timestamp = ?, is_displayed = ?
            WHERE user_id = ?
        """, (user_tag_id, user_name, user_acro, user_time_offset, user_game_start_timestamp, is_displayed_res, user_id))

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@app.route('/admin/add_user', methods=['POST'])
def add_user():
    user_tag_id = request.form.get('user_tag_id')
    user_name = request.form.get('user_name')
    user_acro = request.form.get('user_acro')
    user_time_offset = request.form.get('user_time_offset')
    user_game_start_timestamp = request.form.get('user_game_start_timestamp')
    is_displayed = request.form.get('is_displayed') #returns string "on" or None

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([user_tag_id, user_name, user_acro, user_time_offset, user_game_start_timestamp]):
        return jsonify({"error": "All fields are required."}), 400

    if is_displayed is None:
        is_displayed_res = 0
    else:
        is_displayed_res = 1

    tags = cursor_db.execute('SELECT user_id, user_name FROM users WHERE user_tag_id = ?', (user_tag_id,)).fetchone()
    if tags is not None:
        connection_db.close()
        return jsonify({"error":f"user tag is already in use, by user: {tags[0]}, {tags[1]}"}), 400

    if not user_time_offset.isdecimal():
        return jsonify({"error":"offset must me integers"})

    try:
        insert_user(cursor_db, user_tag_id, user_name, user_acro, user_time_offset, user_game_start_timestamp, is_displayed_res)
        connection_db.commit()
    except sqlite3.Error as e:
        connection_db.close()
        return jsonify({"error": f"An error occurred during inserting: {e}"}), 400
    finally:
        connection_db.close()

    return jsonify({"status": "succes"})


@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


@app.route('/bulk_add_user_time', methods=['POST'])
def bulk_add_user_time():
    data = request.get_json()
    user_ids = data.get('user_ids')
    time_offset = data.get('time_offset')

    if not user_ids or not time_offset:
        return jsonify({"error": "user_ids and time_offset are required"}), 400

    symbol = '+'
    if not time_offset[-1].isdecimal():
        if symbol not in ALLOWED_OPERATORS:
            return jsonify({"error": "time_offset must be an integer"}), 400
        symbol = time_offset[-1]
        time_offset = time_offset[:-1]


    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for user_id in user_ids:
            cursor_db.execute("SELECT user_time_offset FROM users WHERE user_id = ?", (user_id,))
            user = cursor_db.fetchone()

            if user:
                current_offset = user[0]
                new_offset = count_new_offset(current_offset, time_offset, symbol)
                cursor_db.execute("UPDATE users SET user_time_offset = ? WHERE user_id = ?", (new_offset, user_id))

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


# --------------------------- coins -------------------------------------------
@app.route('/admin/coins', methods=['GET'])
def admin_coins():
    connection_db = sqlite3.connect(DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()
    #rows = cursor_db.execute('SELECT * FROM (coins JOIN coin_category ON coins.coin_category = coin_category.coin_category_id) ').fetchall()
    rows = cursor_db.execute("""SELECT coins.coin_id, coins.coin_tag_id, coins.coin_value, coins.last_used, coins.is_active,
       coin_category.coin_category_id, coin_category.coin_category_name
        FROM coins
        JOIN coin_category ON coins.coin_category = coin_category.coin_category_id
    """).fetchall()    
    
    connection_db.close()

    return render_template('admin_coins_tmp.html', coins=rows)
    

@app.route('/admin/update_coin', methods=['POST'])
def update_coin():
    elem_id = request.form.get('coin_id')
    elem_tag_id = request.form.get('coin_tag_id')
    elem_value = request.form.get('coin_value')
    elem_category = request.form.get('coin_category')
    elem_last_used = request.form.get('last_used')
    elem_is_active = request.form.get('is_active')

    if elem_is_active is None:
        elem_is_active_int = 0
    else:
        elem_is_active_int = 1

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_tag_id, elem_value, elem_category, elem_last_used]):
        return jsonify({"error": "All fields are required."}), 400

    tags = cursor_db.execute('SELECT coin_id FROM coins WHERE coin_tag_id = ?', (elem_tag_id,)).fetchone()
    if tags is not None and tags[0] != int(elem_id):
        connection_db.close()
        return jsonify({"error":f"coin tag is already in use, by : {tags[0]}"}), 400

    if not elem_category.isnumeric() or not elem_value.isnumeric():
        return jsonify({"error":"category and offset must me integers"})

    try:
        cursor_db.execute("""
            UPDATE coins
            SET coin_tag_id = ?, coin_value = ?, coin_category = ?, last_used = ?, is_active = ?
            WHERE coin_id = ?
        """, (elem_tag_id, elem_value, elem_category, elem_last_used, elem_is_active_int, elem_id))

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@app.route('/admin/add_coin', methods=['POST'])
def add_coin():
    elem_tag_id = request.form.get('coin_tag_id')
    elem_value = request.form.get('coin_value')
    elem_category = request.form.get('coin_category')
    elem_last_used = request.form.get('last_used')
    elem_activity = request.form.get('is_active')

    if elem_activity is None:
        elem_activity_int = 0
    else:
        elem_activity_int = 1

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_tag_id, elem_value, elem_category, elem_last_used]):
        return jsonify({"error": "All fields are required."}), 400

    tags = cursor_db.execute('SELECT coin_id FROM coins WHERE coin_tag_id = ?', (elem_tag_id,)).fetchone()
    if tags is not None:
        connection_db.close()
        return jsonify({"error":f"coin tag is already in use, by: {tags[0]}"}), 400

    if not elem_category.isnumeric() or not elem_value.isnumeric():
        return jsonify({"error":"category and value must me integers"})

    try:
        insert_coin(cursor_db, elem_tag_id, elem_value, elem_category, elem_last_used, elem_activity_int)
        connection_db.commit()
    except sqlite3.Error as e:
        connection_db.close()
        return jsonify({"error": f"An error occurred during inserting: {e}"}), 400
    finally:
        connection_db.close()

    return jsonify({"status": "succes"})


@app.route('/admin/delete_coin', methods=['POST'])
def delete_coin():
    elem_id = request.form.get('coin_id')
    if not elem_id:
        return jsonify({"error": "coin_id is required"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM coins WHERE coin_id = ?", (elem_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()

@app.route('/bulk_set_coin_field', methods=['POST'])
def bulk_set_coin_field():
    data = request.get_json()
    coin_ids = data.get('coin_ids')
    field_name = data.get('field_name')
    new_value = data.get('new_value')

    if not coin_ids or not field_name or not new_value:
        return jsonify({"error": "coin_ids, field_name, and new_value are required"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
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


@app.route('/bulk_add_coin_time', methods=['POST'])
def bulk_add_coin_time():
    data = request.get_json()
    elem_ids = data.get('coin_ids')
    time_offset = data.get('time_offset')

    if not elem_ids or not time_offset:
        return jsonify({"error": "elem_ids and time_offset are required"}), 400

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            cursor_db.execute("SELECT coin_value FROM coins WHERE coin_id = ?", (elem_id,))
            elem = cursor_db.fetchone()

            if elem:
                current_offset = elem[0]
                new_offset = current_offset + time_offset
                cursor_db.execute("UPDATE coins SET coin_value = ? WHERE coin_id = ?", (new_offset, elem_id))

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


# ---------------------------users categories ---------------------------------
@app.route('/admin/categories_user', methods=['GET'])
def admin_user_categories():
    connection_db = sqlite3.connect(DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute('SELECT * FROM users_category').fetchall()
    
    connection_db.close()

    return render_template('admin_cat_users_tmp.html', categories=rows)
    

@app.route('/admin/update_user_category', methods=['POST'])
def update_user_category():
    elem_id = request.form.get('category_id')
    elem_name = request.form.get('category_name')

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_name]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute("""
            UPDATE users_category
            SET user_category_name = ?
            WHERE user_category_id = ?
        """, (elem_name, elem_id))

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@app.route('/admin/add_user_category', methods=['POST'])
def add_user_category():
    elem_name = request.form.get('category_name')

    connection_db = sqlite3.connect(DATABASE_NAME)
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


@app.route('/admin/delete_user_category', methods=['POST'])
def delete_user_category():
    elem_id = request.form.get('category_id')
    if not elem_id:
        return jsonify({"error": "id is required"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM users_category WHERE user_category_id = ?", (elem_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


@app.route('/bulk_add_user_time_category', methods=['POST'])
def bulk_add_user_time_category():
    data = request.get_json()
    elem_ids = data.get('ids')
    time_offset = data.get('time_offset')

    if not elem_ids or not time_offset:
        return jsonify({"error": "elem_ids and time_offset are required"}), 400

    symbol = '+'
    if not time_offset[-1].isdecimal():
        symbol = time_offset[-1]
        if symbol not in ALLOWED_OPERATORS:
            return jsonify({"error": "time_offset must be an integer"}), 400
        time_offset = time_offset[:-1]

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            cursor_db.execute("""SELECT users.user_id, user_time_offset 
                              FROM users JOIN categories_rel ON users.user_id = categories_rel.user_id
                              WHERE categories_rel.category_id = ?""", (elem_id,))
            elems = cursor_db.fetchall()

            for elem in elems:
                current_offset = elem[1]
                #new_offset = current_offset + time_offset
                new_offset = count_new_offset(current_offset, time_offset, symbol)
                cursor_db.execute("""UPDATE users 
                                  SET user_time_offset = ? 
                                  WHERE user_id = ?""", (new_offset, elem[0]))

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()

# -------------------- users category relations--------------------------------
@app.route('/admin/user_cat_relation', methods=['GET'])
def admin_user_cat_relation():
    connection_db = sqlite3.connect(DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute("""SELECT categories_rel.id, categories_rel.user_id, users.user_name,
                                        categories_rel.category_id, users_category.user_category_name
                                    FROM categories_rel
                                        JOIN users ON users.user_id = categories_rel.user_id
                                        JOIN users_category ON users_category.user_category_id = categories_rel.category_id;
                             """).fetchall()

    connection_db.close()

    return render_template('admin_cat_rel_tmp.html', input_data=rows)

@app.route('/admin/add_user_cat_rel', methods=['POST'])
def add_user_cat_rel():
    user_id_str = request.form.get('user_id')
    cat_id_str = request.form.get('category_id')

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([user_id_str, cat_id_str]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute("""
            INSERT INTO categories_rel (user_id, category_id)
                    VALUES (?, ?)
        """, (int(user_id_str), int(cat_id_str)))

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@app.route('/admin/update_user_cat_rel', methods=['POST'])
def update_user_cat_rel():
    row_id = request.form.get('row_id')
    user_id_str = request.form.get('user_id')
    cat_id_str = request.form.get('category_id')

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([user_id_str, cat_id_str]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute("""
            UPDATE categories_rel
            SET user_id = ?, category_id = ?
            WHERE id = ?
        """, (int(user_id_str), int(cat_id_str), int(row_id)))

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@app.route('/admin/delete_user_cat_rel', methods=['POST'])
def delete_user_cat_rel():
    elem_id = request.form.get('row_id')
    if not elem_id:
        return jsonify({"error": "id is required"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
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
@app.route('/admin/user_cat_relation_v02', methods=['GET'])
def admin_user_cat_relation_v02():
    connection_db = sqlite3.connect(DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    users_rows = cursor_db.execute("""SELECT user_id, user_name FROM users""").fetchall()
    categories_rows = cursor_db.execute("""SELECT user_category_id, user_category_name FROM users_category""").fetchall()
    rel_rows = cursor_db.execute("""SELECT * FROM categories_rel""").fetchall()


    connection_db.close()

    return render_template('admin_cat_rel_tmp_v02.html', users=users_rows, categories=categories_rows, relation=rel_rows)


@app.route('/admin/toggle_user_cat_rel', methods=['POST'])
def toggle_user_cat_rel():
    user_id = request.form.get('user_id')
    category_id = request.form.get('category_id')
    is_checked = request.form.get('is_checked') == 'on'

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if is_checked:
        cursor_db.execute("INSERT INTO categories_rel (user_id, category_id) VALUES (?, ?)", (user_id, category_id))
    else:
        cursor_db.execute("DELETE FROM categories_rel WHERE user_id = ? AND category_id = ?", (user_id, category_id))

    connection_db.commit()
    connection_db.close()

    return jsonify({"message": "Operation successful!"})


# --------------------------------------- coin categories----------------------
# almost identical to users category
@app.route('/admin/categories_coin', methods=['GET'])
def admin_coin_categories():
    connection_db = sqlite3.connect(DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute('SELECT * FROM coin_category').fetchall()

    connection_db.close()

    return render_template('admin_cat_coin_tmp.html', categories=rows)
    

@app.route('/admin/update_coin_category', methods=['POST'])
def update_coin_category():
    elem_id = request.form.get('category_id')
    elem_name = request.form.get('category_name')

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_name]):
        return jsonify({"error": "All fields are required."}), 400

    try:
        cursor_db.execute("""
            UPDATE coin_category
            SET coin_category_name = ?
            WHERE coin_category_id = ?
        """, (elem_name, elem_id))

        connection_db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": f"error: {e}"})
    finally:
        connection_db.close()

    return jsonify({"status": "success"})


@app.route('/admin/add_coin_category', methods=['POST'])
def add_coin_category():
    elem_name = request.form.get('category_name')

    connection_db = sqlite3.connect(DATABASE_NAME)
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


@app.route('/admin/delete_coin_category', methods=['POST'])
def delete_coin_category():
    elem_id = request.form.get('category_id')
    if not elem_id:
        return jsonify({"error": "id is required"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM coin_category WHERE coin_category_id = ?", (elem_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()


@app.route('/bulk_add_coin_time_category', methods=['POST'])
def bulk_add_coin_time_category():
    data = request.get_json()
    elem_ids = data.get('ids')
    time_offset = data.get('time_offset')

    if not elem_ids or not time_offset:
        return jsonify({"error": "elem_ids and time_offset are required"}), 400
    
    symbol = '+'
    if not time_offset[-1].isdecimal():
        symbol = time_offset[-1]
        if symbol not in ALLOWED_OPERATORS:
            return jsonify({"error": "time_offset must be an integer"}), 400
        time_offset = time_offset[:-1]

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            cursor_db.execute("SELECT coin_id, coin_value FROM coins WHERE coin_category = ?", (elem_id,))
            elems = cursor_db.fetchall()

            for elem in elems:
                current_offset = elem[1]
                new_offset = count_new_offset(current_offset, time_offset, symbol)
                cursor_db.execute("UPDATE coins SET coin_value = ? WHERE coin_id = ?", (new_offset, elem[0]))

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()

# --------------------------------- other--------------------------------------
@app.route('/show_logs', methods=['GET'])
def show_logs():
    user = request.args.get('user_id')


    if user and not user.isnumeric():
        return jsonify({"status": "error", "message": "wrong user id"}), 500
    
    connection_db = sqlite3.connect(DATABASE_NAME)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    if user is None or user == "":
        rows = cursor_db.execute('SELECT * FROM (logs JOIN users ON logs.user_id = users.user_id) ORDER BY id DESC').fetchall()
    else:
        rows = cursor_db.execute('SELECT * FROM (logs JOIN users ON logs.user_id = users.user_id) WHERE logs.user_id = ? ORDER BY id DESC', (user,)).fetchall()
    
    connection_db.close()

    return render_template('logs_tmp.html', logs=rows)


@app.route('/get_logs', methods=['GET'])
def show_logs_json():
    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    cursor_db.execute("""SELECT * FROM logs """)
    result = cursor_db.fetchall()

    connection_db.close()

    return result


@app.route('/show_times', methods=['GET'])
def show_times():
    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute("""SELECT user_name, user_time_offset, user_game_start_timestamp FROM users """).fetchall()
    connection_db.close()

    result = []

    for name, offset, start in rows:
        time_int = offset - (datetime.now() - datetime.fromisoformat(start)).total_seconds()
        temp_dict = {}
        temp_dict['name'] = name
        temp_dict['time'] = seconds_to_text(time_int)
        result.append(temp_dict)

    return render_template("times_tiles_tmp.html", users=result)


@app.route('/show_times_02', methods=['GET'])
def show_times_02():
    return render_template("times_tiles_v02.html")


@app.route('/show_times_api', methods=['GET'])
def api_times_init():
    connection_db = sqlite3.connect(DATABASE_NAME)
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute("""
        SELECT user_name, user_time_offset, user_game_start_timestamp, is_displayed
        FROM users
    """).fetchall()
    connection_db.close()

    result = []
    for name, offset, start, is_disp in rows:
        if is_disp == 0:
            continue
        result.append({
            'name': name,
            'offset': offset,
            'start': start  # ISO format is fine
        })
    return jsonify(result)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print("start")
    create_tables(DATABASE_NAME)
    app.run(host='0.0.0.0', debug=True)
