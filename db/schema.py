import sqlite3


def create_user_db(cur):
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_tag_id TEXT,
        user_name TEXT,
        user_acro TEXT,
        user_time_offset INTEGER,
        user_game_start_timestamp DATETIME,
        is_displayed BOOLEAN
    )
    """
    )


def create_category_db(cur):
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users_category (
        user_category_id INTEGER PRIMARY KEY,
        user_category_name TEXT
    )"""
    )

    cur.execute(
        """
    INSERT OR IGNORE INTO
                users_category (user_category_id, user_category_name)
                VALUES (0, 'no_category')
    """
    )


def create_coins_db(cur):
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS coins (
        coin_id INTEGER PRIMARY KEY,
        coin_tag_id TEXT,
        coin_value INTEGER,
        coin_category INTEGER,
        last_used DATETIME,
        is_active BOOLEAN
    )"""
    )


def create_coin_category_db(cur):
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS coin_category (
        coin_category_id INTEGER PRIMARY KEY,
        coin_category_name TEXT
    )"""
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO
                coin_category (coin_category_id, coin_category_name)
                VALUES (0, 'no_category')
    """
    )


def create_log_table(cur):
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME,
        user_id INTEGER,
        amount INTEGER,
        details TEXT
    )"""
    )


def create_log_triggers(cur):
    cur.execute(
        """
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
    """
    )


def create_categories_relation(cur):
    # one to many relation
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS categories_rel (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        category_id INTEGER
    )"""
    )


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
