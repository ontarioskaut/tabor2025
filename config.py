# common
DATABASE_NAME = "database.db"
ALLOWED_OPERATORS = {"+", "-", "*", "%", "d", "h", "s"}

# show_times live page
WEB_REFRESH_INTERVAL = 2000

# displays
DISPLAYS = [
    {
        "name": "buse5p",
        "color": False,
        "resolution": (140, 19),
        "announcements": True,
        "time": True,
        "fit_times": 4,
        "engine": "buse5p",
    },
    {
        "name": "buse4p",
        "color": False,
        "resolution": (112, 19),
        "announcements": True,
        "time": True,
        "fit_times": 4,
        "engine": "buse4p",
    },
]

DISPLAY_TIME_SCREEN_DURATION = 3
DISPLAY_STATE_DIR = "/tmp/intime/"
