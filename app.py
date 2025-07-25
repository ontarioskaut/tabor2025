#!/usr/bin/env python3
#import json
from flask import Flask, jsonify, request, render_template, render_template_string
import sqlite3
from datetime import datetime


database_name = "database.db"



#connection_db = sqlite3.connect("database.db")
#cursor_db = connection_db.cursor()

def create_user_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_tag_id TEXT,
        user_name TEXT,
        user_acro TEXT,
        user_category INTEGER,
        user_time_offset INTEGER,
        user_game_start_timestamp DATETIME,
        is_displayed INTEGER
    )
    """)
def create_category_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users_category (
        user_category_id INTEGER PRIMARY KEY,
        user_category_name TEXT
    )""")

def create_coins_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coins (
        coin_id INTEGER PRIMARY KEY,
        coin_tag_id TEXT,
        coin_value INTEGER,
        coin_category INTEGER
    )""")
    
def create_coin_category_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coin_category (
        coin_category_id INTEGER PRIMARY KEY,
        coin_category_name TEXT
    )""")

def create_tables(name: str):
    connection_db = sqlite3.connect(name)
    cursor_db = connection_db.cursor()
    create_user_db(cursor_db)
    create_coins_db(cursor_db)
    create_category_db(cursor_db)
    create_coin_category_db(cursor_db)
    cursor_db.close()


def insert_user(cur, tag_id: str, name: str, acro: str, category: int, offset: int, start: int, is_displayed: int):
    cur.execute(f"SELECT MAX(user_id) FROM users")
    new_id = cur.fetchone()[0]
    new_id = new_id + 1 if new_id is not None else 1
    temp = f"{new_id}, '{tag_id}', '{name}', '{acro}', {category}, {offset}, '{start}', {is_displayed}"
    cur.execute("Insert INTO users VALUES (" + temp + ")")

    
def insert_coin(cur, tag_id: str, value: int, category: int):
    cur.execute(f"SELECT MAX(coin_id) FROM coins")
    new_id = cur.fetchone()[0]
    new_id = new_id + 1 if new_id is not None else 1
    temp = f"{new_id}, '{tag_id}', {value}, {category}"
    cur.execute("Insert INTO coins VALUES (" + temp + ")")



def test_show_users(cur):
    test = cur.execute("SELECT * from users")
    print(test.fetchall())


def test_fce():
    print("running this")
    #create_tables(database_name)

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()
    #insert_user(cursor_db, 1, 10, "alfa", "a", 5, 10000, datetime.now())
    #insert_user(cursor_db, 2, 20, "beta", "b", 2, 20000, datetime.now())

    insert_coin(cursor_db, 1, "A1", 1000, 4)
    insert_coin(cursor_db, 2, "B1", 2000, 2)

    connection_db.commit()

    #test = cursor_db.execute("sqlite_master")
    test = cursor_db.execute("SELECT * from users")
    print(test.fetchall())


    print("heeej")

#test_fce()

#------------------------------------------------------------------------------
# --------------FLASK-------------------------------------------
#------------------------------------------------------------------------------
app = Flask(__name__, static_url_path='/static', static_folder='static')
@app.route('/')
def index():
    return "hello world"

#------------------------------------------------------------------------------
# ------------------API FOR NODES------------------------------
#------------------------------------------------------------------------------
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
        time_diff = (datetime.now() - datetime.fromisoformat(start_str)).total_seconds()
        time = -round(time_diff) + int(offset)
        return jsonify({"name":name, "user_time": time})
    else:
        return jsonify({"error": "User not found"}), 404


def addition_of_time(user_tag_id, time_to_change, is_addition: bool):
    if not time_to_change or not user_tag_id:
        return jsonify({"error": "time_to_subtract and user_tag_id are required"}), 400
    
    try:
        time_to_change = int(time_to_change)
    except ValueError:
        return jsonify({"error": "time must be an integer"}), 400

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT user_time_offset FROM users WHERE user_tag_id = ?", (user_tag_id,))
    user = cursor_db.fetchone()

    if user:
        current_offset = user[0]
        if not is_addition:
            time_to_change *= -1
        new_offset = current_offset + time_to_change
        cursor_db.execute("UPDATE users SET user_time_offset = ? WHERE user_tag_id = ?", (new_offset, user_tag_id))
        connection_db.commit()
        connection_db.close()

        return jsonify({"status": "success", "user_time": new_offset})
    else:
        connection_db.close()
        return jsonify({"error": "User not found"}), 404


@app.route('/subtract_time', methods=['GET'])
def substract_time():
    time_to_subtract = request.args.get('time_to_subtract')
    user_tag_id = request.args.get('user_tag_id')

    print(time_to_subtract)
    print(user_tag_id)

    return addition_of_time(user_tag_id, time_to_subtract, False)


@app.route('/add_time', methods=['GET'])
def add_time():
    time_to_add = request.args.get('time_to_add')
    user_tag_id = request.args.get('user_tag_id')

    return addition_of_time(user_tag_id, time_to_add, True)



@app.route('/add_coinval', methods=['GET'])
def add_coinval():
    coin_tag_id = request.args.get('coin_tag_id')
    user_tag_id = request.args.get('user_tag_id')
    if not coin_tag_id or not user_tag_id:
        return jsonify({"error": "coin_tag_id and user_tag_id are required"}), 400

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT user_time_offset FROM users WHERE user_tag_id = ?", (user_tag_id,))
    user = cursor_db.fetchone()


    cursor_db.execute("SELECT coin_value FROM coins WHERE coin_tag_id = ?", (coin_tag_id,))
    coin = cursor_db.fetchone()


    if user and coin:
        new_offset = coin[0] + user[0]
        cursor_db.execute("UPDATE users SET user_time_offset = ? WHERE user_tag_id = ?", (new_offset, user_tag_id))
        connection_db.commit()
        connection_db.close()
        return jsonify({"status": "success", "user_time": new_offset})

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

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT coin_tag_id FROM coins WHERE coin_tag_id = ?", (coin_tag_id,))
    user = cursor_db.fetchone()
    if user is not None: # coin_tag_id is already in database
        cursor_db.execute("UPDATE coins SET coin_value = ?, coin_category = ? WHERE coin_tag_id = ?", (coin_value, category, coin_tag_id))
    else:
        insert_coin(cursor_db, coin_tag_id, coin_value, category)
    
    connection_db.commit()
    connection_db.close()


    return jsonify({"status": "success"})



@app.route('/init_user_tag', methods=['GET'])
def init_user_tag():
    user_tag_id = request.args.get('user_tag_id')

    if not user_tag_id:
        return jsonify({"error": "no user_tag_id"}), 400

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    cursor_db.execute("SELECT user_id FROM users WHERE user_tag_id = ?", (user_tag_id,))
    user = cursor_db.fetchone()


    response = {}

    if user:
        response["status"] = "error"
        response["text"] = "user already exist"
    else:
        #cursor_db.execute(f"SELECT MAX(user_id) FROM users")
        #line_count = cursor_db.fetchone()[0]
        response["status"] = "success"

        insert_user(cursor_db, user_tag_id, "initname", "x", 0, 0, datetime.now(), 0)
    
    connection_db.commit()
    connection_db.close()

    return jsonify(response)


#------------------------------------------------------------------------------
#-----------------------------Display api--------------
#------------------------------------------------------------------------------
@app.route('/get_time', methods=['GET'])
def get_time():
    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()
    cursor_db.execute("SELECT user_acro, user_time_offset, user_game_start_timestamp, is_displayed FROM users")
    rows = cursor_db.fetchall()
    connection_db.close()

    user_dict = {}


    for acro, offset, start, disp in rows:
        if int(disp) == 0:
            continue
        time_diff = (datetime.now() - datetime.fromisoformat(start)).total_seconds()

        user_dict[acro] = -round(time_diff) + int(offset)

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

    connection_db = sqlite3.connect(database_name)
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
    <html>
    <head>
        <title>Admin Dashboard</title>
    </head>
    <body>
        <h1>Welcome to the Admin Dashboard</h1>
        <ul>
            <li><a href="/admin/users">Users</a></li>
            <li><a href="/admin/coins">Coins</a></li>
            <li><a href="/admin/categories_user">user categories</a></li>
            <li><a href="/admin/categories_coin">Locoin categoriesgs</a></li>
        </ul>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/admin/users', methods=['GET'])
def admin_users():
    connection_db = sqlite3.connect(database_name)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()


    rows = cursor_db.execute('SELECT * FROM users').fetchall()
    
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

    #return render_template('user_db_tmp.html', users=rows)
    return render_template('admin_users_tmp.html', users=user_rows, current_time=current_time)
    
@app.route('/admin/update_user', methods=['POST'])
def update_user():
    user_id = request.form.get('user_id')
    user_tag_id = request.form.get('user_tag_id')
    user_name = request.form.get('user_name')
    user_acro = request.form.get('user_acro')
    user_category = request.form.get('user_category')
    user_time_offset = request.form.get('user_time_offset')
    user_game_start_timestamp = request.form.get('user_game_start_timestamp')
    is_displayed = request.form.get('is_displayed')
    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not all([user_tag_id, user_name, user_acro, user_category, user_time_offset, user_game_start_timestamp]):
        return jsonify({"error": "All fields are required."}), 400

    if is_displayed is None:
        is_displayed_res = 0
    else:
        is_displayed_res = 1

    tags = cursor_db.execute('SELECT user_id, user_name FROM users WHERE user_tag_id = ?', (user_tag_id,)).fetchone()
    if tags is not None and tags[0] != int(user_id):
        connection_db.close()
        return jsonify({"error":f"user tag is already in use, by user: {tags[0]}, {tags[1]}"}), 400

    if not user_category.isnumeric() or not user_time_offset.isnumeric():
        return jsonify({"error":"category and offset must me integers"})

    try:
        cursor_db.execute("""
            UPDATE users
            SET user_tag_id = ?, user_name = ?, user_acro = ?, user_category = ?, user_time_offset = ?, user_game_start_timestamp = ?, is_displayed = ?
            WHERE user_id = ?
        """, (user_tag_id, user_name, user_acro, user_category, user_time_offset, user_game_start_timestamp, is_displayed_res, user_id))

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
    user_category = request.form.get('user_category')
    user_time_offset = request.form.get('user_time_offset')
    user_game_start_timestamp = request.form.get('user_game_start_timestamp')
    is_displayed = request.form.get('is_displayed')

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not all([user_tag_id, user_name, user_acro, user_category, user_time_offset, user_game_start_timestamp]):
        return jsonify({"error": "All fields are required."}), 400

    if is_displayed is None:
        is_displayed_res = 0
    else:
        is_displayed_res = 1

    tags = cursor_db.execute('SELECT user_id, user_name FROM users WHERE user_tag_id = ?', (user_tag_id,)).fetchone()
    if tags is not None:
        connection_db.close()
        return jsonify({"error":f"user tag is already in use, by user: {tags[0]}, {tags[1]}"}), 400

    if not user_category.isnumeric() or not user_time_offset.isnumeric():
        return jsonify({"error":"category and offset must me integers"})

    try:
        insert_user(cursor_db, user_tag_id, user_name, user_acro, user_category, user_time_offset, user_game_start_timestamp, is_displayed_res)
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

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()
    try:
        cursor_db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        connection_db.close()

# @app.route('/bulk_set_coin_field', methods=['POST'])
# def bulk_set_coin_field():
#     data = request.get_json()
#     coin_ids = data.get('coin_ids')
#     field_name = data.get('field_name')
#     new_value = data.get('new_value')

#     if not coin_ids or not field_name or not new_value:
#         return jsonify({"error": "coin_ids, field_name, and new_value are required"}), 400

#     connection_db = sqlite3.connect(database_name)
#     cursor_db = connection_db.cursor()

#     try:
#         for coin_id in coin_ids:
#             query = f"UPDATE coins SET {field_name} = ? WHERE coin_id = ?"
#             cursor_db.execute(query, (new_value, coin_id))

#         connection_db.commit()
#         return jsonify({"status": "success"})
#     except sqlite3.Error as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
#     finally:
#         connection_db.close()

@app.route('/bulk_add_user_time', methods=['POST'])
def bulk_add_user_time():
    data = request.get_json()
    user_ids = data.get('user_ids')
    time_offset = data.get('time_offset')

    if not user_ids or not time_offset:
        return jsonify({"error": "user_ids and time_offset are required"}), 400

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    try:
        for user_id in user_ids:
            cursor_db.execute("SELECT user_time_offset FROM users WHERE user_id = ?", (user_id,))
            user = cursor_db.fetchone()

            if user:
                current_offset = user[0]
                new_offset = current_offset + time_offset
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
    connection_db = sqlite3.connect(database_name)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute('SELECT * FROM coins').fetchall()
    
    connection_db.close()

    return render_template('admin_coins_tmp.html', coins=rows)
    

@app.route('/admin/update_coin', methods=['POST'])
def update_coin():
    elem_id = request.form.get('coin_id')
    elem_tag_id = request.form.get('coin_tag_id')
    elem_value = request.form.get('coin_value')
    elem_category = request.form.get('coin_category')

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_tag_id, elem_value, elem_category]):
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
            SET coin_tag_id = ?, coin_value = ?, coin_category = ?
            WHERE coin_id = ?
        """, (elem_tag_id, elem_value, elem_category, elem_id))

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

    print("hej")
    print(elem_tag_id)
    print(elem_value)
    print(elem_category)

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not all([elem_tag_id, elem_value, elem_category]):
        return jsonify({"error": "All fields are required."}), 400

    tags = cursor_db.execute('SELECT coin_id FROM coins WHERE coin_tag_id = ?', (elem_tag_id,)).fetchone()
    if tags is not None:
        connection_db.close()
        return jsonify({"error":f"coin tag is already in use, by: {tags[0]}"}), 400

    if not elem_category.isnumeric() or not elem_value.isnumeric():
        return jsonify({"error":"category and value must me integers"})

    try:
        insert_coin(cursor_db, elem_tag_id, elem_value, elem_category)
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

    connection_db = sqlite3.connect(database_name)
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

    connection_db = sqlite3.connect(database_name)
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

    print("workign here")

    if not elem_ids or not time_offset:
        return jsonify({"error": "elem_ids and time_offset are required"}), 400

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            cursor_db.execute("SELECT coin_value FROM coins WHERE coin_id = ?", (elem_id,))
            elem = cursor_db.fetchone()

            if elem:
                current_offset = elem[0]
                new_offset = current_offset + time_offset
                cursor_db.execute("UPDATE coins SET coin_value = ? WHERE coin_id = ?", (new_offset, elem_id))
                print("even here")

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


# --------------------------- categories -------------------------------------------


@app.route('/admin/categories_user', methods=['GET'])
def admin_user_categories():
    connection_db = sqlite3.connect(database_name)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute('SELECT * FROM users_category').fetchall()
    
    connection_db.close()

    return render_template('admin_cat_users_tmp.html', categories=rows)
    

@app.route('/admin/update_user_category', methods=['POST'])
def update_user_category():
    elem_id = request.form.get('category_id')
    elem_name = request.form.get('category_name')

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_name]):
        return jsonify({"error": "All fields are required."}), 400

    print(elem_id)
    print(elem_name)

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

    print(elem_name)

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not elem_name:
        return jsonify({"error": "Name is required."}), 400

    try:
        cursor_db.execute(f"SELECT MAX(user_category_id) FROM users_category")
        new_id = cursor_db.fetchone()[0]
        new_id = new_id + 1 if new_id is not None else 1
        print(new_id)
        temp = f"{new_id}, '{elem_name}'"
        print(temp)
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

    connection_db = sqlite3.connect(database_name)
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

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    print(elem_ids)

    try:
        for elem_id in elem_ids:
            print(elem_id)
            cursor_db.execute("SELECT user_id, user_time_offset FROM users WHERE user_category = ?", (elem_id,))
            elems = cursor_db.fetchall()

            print("printing elems:")
            print(elems)

            for elem in elems:
                current_offset = elem[1]
                new_offset = current_offset + time_offset
                cursor_db.execute("UPDATE users SET user_time_offset = ? WHERE user_id = ?", (new_offset, elem[0]))
                print("even here")

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()


# --------------------------------------- coin categories----------------------
#takže to celé ještě jednou ale lehce upravené

@app.route('/admin/categories_coin', methods=['GET'])
def admin_coin_categories():
    connection_db = sqlite3.connect(database_name)
    connection_db.row_factory = sqlite3.Row
    cursor_db = connection_db.cursor()

    rows = cursor_db.execute('SELECT * FROM coin_category').fetchall()
    
    connection_db.close()

    for row in rows:
        print(row['coin_category_id'])
        print(row['coin_category_name'])

    return render_template('admin_cat_coin_tmp.html', categories=rows)
    

@app.route('/admin/update_coin_category', methods=['POST'])
def update_coin_category():
    print("update coin category")
    elem_id = request.form.get('category_id')
    elem_name = request.form.get('category_name')

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not all([elem_id, elem_name]):
        return jsonify({"error": "All fields are required."}), 400

    print("printing in upadate")
    print(elem_id)
    print(elem_id)

    print(elem_name)

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

    print(elem_name)

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    if not elem_name:
        return jsonify({"error": "Name is required."}), 400
    

    try:
        cursor_db.execute(f"SELECT MAX(coin_category_id) FROM coin_category")
        new_id = cursor_db.fetchone()[0]
        new_id = new_id + 1 if new_id is not None else 1
        print(new_id)
        temp = f"{new_id}, '{elem_name}'"
        print(temp)
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

    connection_db = sqlite3.connect(database_name)
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

    try:
        time_offset = int(time_offset)
    except ValueError:
        return jsonify({"error": "time_offset must be an integer"}), 400

    connection_db = sqlite3.connect(database_name)
    cursor_db = connection_db.cursor()

    try:
        for elem_id in elem_ids:
            print(elem_id)
            cursor_db.execute("SELECT coin_id, coin_value FROM coins WHERE coin_category = ?", (elem_id,))
            elems = cursor_db.fetchall()

            for elem in elems:
                current_offset = elem[1]
                new_offset = current_offset + time_offset
                cursor_db.execute("UPDATE coins SET coin_value = ? WHERE coin_id = ?", (new_offset, elem[0]))

        connection_db.commit()
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection_db.close()

if __name__ == '__main__':
    print("start")
    create_tables(database_name)
    app.run(host='0.0.0.0', debug=True)

