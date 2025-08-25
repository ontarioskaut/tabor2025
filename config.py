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


GAME_CODE = 123
GAME_SAFE_ALLOWED = True

SYSTEM_ACTIVE = True
INACTIVE_ANNOUNCEMENT = "iVBORw0KGgoAAAANSUhEUgAAAIwAAAATCAIAAADNknL/AAAABmJLR0QA/wD/AP+gvaeTAAABTElEQVRYhe1Y2Q4CIQy0m/3/X14fMEhaOi2H7GI6LyrHdKAXka7regWejeNuAQEb4aQNcKYPImITrWVQMpRUeTaqawc+mRR3VwURgeBbJ6N0TxI06LB/SpopFzKOE8xliWU09SlmngPMwJYpAxRtNgWYpRLmKo1KRicYkYPgnu2HA9M0Mf0ls0YupwZllNurVH5+50rzCOAnyqQMGeOzoGVPGiEiFvKe2apUWdXZdkml1W2NiqUCYMYaJEnDE/x3pTkzmyY8nbyvKU58I2QH9BmSsl2ZBKQA6nuBuw5bqbWfKpxUE9HvpPXwxAFuMFo98ddzk6q6jBlqRb+T1qeObEJyQfpSXWYK9udB99nNI1TxdVJTyi9Gvj7nA73qLTPqTaPgYSJ3MeueI2g4TKsPwUjQNO3VFqfxZTJK9GRfYDHiX/ANEE7aAOGkDfAG2JP/XyNSh64AAAAASUVORK5CYII="
ALLOCATED_TIME = 50 * 365 * 24 * 60 * 60
