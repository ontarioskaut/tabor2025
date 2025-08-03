from datetime import datetime


def insert_user(
    cur, tag_id: str, name: str, acro: str, offset: int, start: str, is_displayed: int
):
    cur.execute("SELECT MAX(user_id) FROM users")
    new_id = cur.fetchone()[0]
    new_id = new_id + 1 if new_id else 1
    cur.execute(
        """
        INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (new_id, tag_id, name, acro, offset, start, is_displayed),
    )


def insert_coin(
    cur,
    tag_id: str,
    value: int,
    category: int,
    last_used="1970-01-01 00:00:00",
    is_active=0,
):
    cur.execute("SELECT MAX(coin_id) FROM coins")
    new_id = cur.fetchone()[0]
    new_id = new_id + 1 if new_id else 1
    cur.execute(
        """
        INSERT INTO coins VALUES (?, ?, ?, ?, ?, ?)
    """,
        (new_id, tag_id, value, category, last_used, is_active),
    )
