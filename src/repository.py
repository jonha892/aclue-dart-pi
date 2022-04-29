from dataclasses import dataclass
import sqlite3
import os
import json

from main import ThrowRequest

# from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer


class Position(object):
    x: float
    y: float


class Label(object):
    anchor_top: Position
    anchor_bottom: Position
    anchor_left: Position
    anchor_right: Position

    darts = []


@dataclass
class Throw(object):
    throw_id: str
    series_id: int
    dart: str
    label: dict  # Label

    @staticmethod
    def from_request(request: ThrowRequest):
        return Throw(request.throw_id, request.series_id, request.dart, {})


THROW_TABLENAME = "throw"
DB_PATH = "../db"
DB_FILENAME = "database.sqlite3"


def init_databse(db_path: str, db_filename: str):
    os.makedirs(db_path, exist_ok=True)

    conn = sqlite3.connect(os.path.join(db_path, db_filename))
    conn.execute(
        'CREATE TABLE IF NOT EXISTS throw (throw_id TEXT, series_id INTEGER NOT NULL, dart TEXT NOT NULL, label TEXT DEFAULT "{}", PRIMARY KEY (throw_id, series_id))'
    )


def drop_table(conn: sqlite3.Connection, table_name: str):
    conn.execute(f"DROP TABLE {table_name}")


def remove_all(conn: sqlite3.Connection, table_name: str):
    conn.execute(f"DELETE FROM {table_name}")


def list_all(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT * FROM throw")
    rows = cur.fetchall()
    print(rows)


def insert_throw(conn: sqlite3.Connection, throw: Throw):
    if throw.label is not None:
        label_json_str = json.dumps(throw.label)
    else:
        label_json_str = "\{\}"

    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO throw (throw_id, series_id, dart, label) VALUES (?, ? ,? ,?)",
        (throw.throw_id, throw.series_id, throw.dart, label_json_str),
    )
    conn.commit()


def get_throw(conn: sqlite3.Connection, throw_id: str, series_id: int):
    cur = conn.cursor()
    cur.execute(
        "SELECT * from throw WHERE throw_id = ? AND series_id = ?",
        (throw_id, series_id),
    )
    rows = cur.fetchall()
    if len(rows) > 1:
        raise ValueError(f"Error expected one row, found {len(rows)}")
    row = rows[0]
    print(row)
    return Throw(row[0], row[1], row[2], json.loads(row[3]))


init_databse(DB_PATH, DB_FILENAME)

conn = sqlite3.connect(os.path.join(DB_PATH, DB_FILENAME))
# drop_table(conn, "throw")
remove_all(conn, "throw")
list_all(conn)

try:
    throw = Throw("test_0", 0, "8", {})
    insert_throw(conn, throw)
    throw = Throw("test_0", 1, "t20", {})
    insert_throw(conn, throw)
    throw = Throw("test_0", 2, "25", {})
    insert_throw(conn, throw)
except sqlite3.IntegrityError:
    print("found duplicate skipping element")
list_all(conn)

e = get_throw(conn, "test_0", 1)
print(e)

# engine = create_engine(f"sqlite://f{DB_PATH}", echo=True)

# if not engine.dialect.has_table(THROW_TABLENAME):
#     metadata = MetaData(engine)
#     throw_table = Table(
#         THROW_TABLENAME,
#         metadata,
#         Column("throw_id", String, primary_key=True),
#         Column("series_id", Integer),
#         Column("dart", String),
#         Column("label", Integer),
#     )
