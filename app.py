#!/usr/bin/env python3
import argparse
import atexit
import threading

from flask import Flask, render_template

import config
from db.schema import create_tables
from display.draw_loop import run_format_loop, run_loop
from routes.api_admin import bp_admin
from routes.api_display import bp_display
from routes.api_misc import bp_misc
from routes.api_nodes import bp_nodes
from routes.pages_admin import bp_admin_pages

app = Flask(__name__, static_url_path="/static", static_folder="static")

# Register blueprints
app.register_blueprint(bp_nodes, url_prefix="/api/nodes")
app.register_blueprint(bp_admin, url_prefix="/api/admin")
app.register_blueprint(bp_admin_pages, url_prefix="/admin")
app.register_blueprint(bp_display, url_prefix="/api/display")
app.register_blueprint(bp_misc, url_prefix="/api/misc")


@app.route("/")
def index():
    return render_template("index.html")


stop_event = threading.Event()
thread = None


def start_background_thread():
    global thread
    if thread is None or not thread.is_alive():
        thread = threading.Thread(
            target=run_loop, args=(stop_event, config), daemon=True
        )
        thread.start()
        print("[Thread] Background draw_loop started")


def start_format_thread():
    global thread
    if thread is None or not thread.is_alive():
        thread = threading.Thread(
            target=run_format_loop, args=(stop_event, config), daemon=True
        )
        thread.start()
        print("[Thread] Background format_loop started")


def stop_background_thread():
    print("[Thread] Stopping background thread...")
    stop_event.set()
    if thread and thread.is_alive():
        thread.join(timeout=2)


atexit.register(stop_background_thread)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InTime server")
    parser.add_argument(
        "--format",
        action="store_true",
        help="Run in display formatting mode (run_format_loop instead of run_loop)",
    )
    args = parser.parse_args()

    print("start")
    create_tables(config.DATABASE_NAME)

    if args.format:
        print("Running in format mode")
        start_format_thread()
    else:
        print("Running in normal mode")
        start_background_thread()

    app.run(
        host="0.0.0.0", debug=True, use_reloader=False, ssl_context=config.SSL_CONTEXT
    )
