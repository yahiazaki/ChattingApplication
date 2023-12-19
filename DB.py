import sqlite3

import bcrypt

"""Table creation"""


def create_table():
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS userdata(
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL
    )
    """)

    conn.commit()
    conn.close()


"""inserting the username and password from the registeration proccess into the database
and hashing the password using salted hash"""


def insert_user(username, password):
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    cur.execute("INSERT INTO userdata(username, password,password_salt) VALUES (?, ?,?)",
                (username, hashed_password, salt))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    # You can also insert initial data here if needed
