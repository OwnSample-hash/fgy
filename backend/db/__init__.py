from .connection import *
from .mariadb import *
from .redis import *
from .models import *
import os

db = MariaDB(
    con=Connection(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    ),
    database=os.environ["DB_NAME"],
)

redis = Redis(
    con=Connection(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ["REDIS_PORT"]),
        username=os.environ.get("REDIS_USER", ""),
        password=os.environ.get("REDIS_PASSWORD", ""),
    ),
    db=int(os.environ.get("REDIS_DB", 0)),
)
