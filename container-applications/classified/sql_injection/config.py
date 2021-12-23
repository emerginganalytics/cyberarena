import hashlib
import os
import sqlite3


def connect_db():
    return sqlite3.connect("bad.db")


def hash_pass(passw):
    m = hashlib.md5()
    m.update(passw.encode('utf-8'))
    return m.hexdigest()


if not os.path.exists("bad.db"):
    with sqlite3.connect("bad.db") as connection:
        c = connection.cursor()
        c.execute("""CREATE TABLE employees(username TEXT, password TEXT)""")
        c.execute('INSERT INTO employees VALUES("RickAstley", "{}")'.format(hash_pass("NeverGonnaGiveYouUp")))
        c.execute('INSERT INTO employees VALUES("SuperSecretClassifiedEmployee", "{}")'.format(hash_pass("password")))
        c.execute('INSERT INTO employees VALUES("BigBossAdmin", "{}")'.format(hash_pass("kittycat222")))
        connection.commit()
