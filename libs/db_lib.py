import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config_reader import config


def conn_db():
    conn = pg.connect(database=config.pg_dbname,
                      user=config.pg_user,
                      password=config.pg_pwd.get_secret_value(),
                      host=config.pg_host,
                      port=5432)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    return conn, cur


def pg_select_one_column(query: str):
    res = []
    conn, cur = conn_db()
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        res.append(row[0])
    cur.close()
    conn.close()
    return res


def pg_select(query: str):
    conn, cur = conn_db()
    cur.execute(query)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res


def pg_execute(query: str):
    conn, cur = conn_db()
    cur.execute(query)
    cur.close()
    conn.close()
