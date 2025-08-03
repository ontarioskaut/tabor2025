#!/usr/bin/env python3
import atexit
import threading

from flask import Flask, render_template

import config
from db.schema import create_tables
from display.draw_loop import run_loop
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


# display thread control
stop_event = threading.Event()
thread = None


def start_background_thread():
    global thread
    if thread is None or not thread.is_alive():
        thread = threading.Thread(target=run_loop, args=(stop_event,), daemon=True)
        thread.start()
        print("Background thread started")


def stop_background_thread():
    print("Stopping background thread...")
    stop_event.set()
    if thread and thread.is_alive():
        thread.join(timeout=2)


# display thread cleanup
atexit.register(stop_background_thread)

if __name__ == "__main__":
    print("start")
    create_tables(config.DATABASE_NAME)
    start_background_thread()
    app.run(host="0.0.0.0", debug=True)
