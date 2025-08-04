# common
DATABASE_NAME = "database.db"

# SSL
# uncomment the first line to test https.
# you will need to create self-signed certs using:
# openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
# SSL_CONTEXT = ('cert.pem', 'key.pem')
SSL_CONTEXT = None

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
DISPLAY_ANNOUNCEMENT_AFTER_N_CYCLES = 2
DISPLAY_ANNOUNCEMENT_DURATION = 3
