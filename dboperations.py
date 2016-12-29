import sqlite3
import datetime


class DBOperations(object):
    """
    Simple wrapper over common SQLite operations.
    """

    def __init__(self, path, type='sqlite'):
        self.type = type
        self.path = path
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def setup(self):
        """
        Creates tables if not already present
        :return: None
        """
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS user (username TEXT UNIQUE NOT NULL, password TEXT, last_login  DATETIME, last_logout DATETIME, online INT);")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS messages (from_user REFERENCES user (username), to_user REFERENCES user (username),content TEXT, timestamp DATETIME);")
        self.connection.commit()

    def add_user(self, username, password):
        """
        Adds a user to the database. Stores password in plain text.
        :param username:
        :param password:
        :return:
        """
        self.cursor.execute("INSERT INTO user VALUES (?,?,?,NULL,?);", (username, password, datetime.datetime.now(), 0))
        self.connection.commit()

    def add_message(self, from_user, to_user, message):
        """
        Adds a message to the message table with appropriate foreign keys
        :param to_user:
        :param from_user:
        :param message:
        :return:
        """
        self.cursor.execute("INSERT INTO messages VALUES (?,?,?,?);",
                            (from_user, to_user, message, datetime.datetime.now()))
        self.connection.commit()

    def update_login(self, username):
        """
        Updates the last login time of a user
        :param username:
        :return:
        """
        self.cursor.execute("UPDATE user SET last_login = ? WHERE username LIKE ?;",
                            (datetime.datetime.now(), username))
        self.connection.commit()

    def update_logout(self, username):
        """
        Updates the last log out time of the user
        :param username:
        :return:
        """
        self.cursor.execute("UPDATE user SET last_logout = ? WHERE username LIKE ?;",
                            (datetime.datetime.now(), username))
        self.connection.commit()

    def return_all_users(self):
        """
        Returns all registered users
        :return:
        """
        return self.cursor.execute("SELECT username FROM user;").fetchall()

    def return_online_users(self):
        """
        Returns all users who are online
        :return:
        """
        return self.cursor.execute("SELECT username FROM user WHERE online = 1;").fetchall()

    def auth_user(self, username, password):
        """
        Attempts to authenticate credentials against a database
        :param username:
        :param password:
        :return: 0 or 1 (Boolean)
        """
        return len(self.cursor.execute('SELECT * FROM user WHERE username LIKE ? AND password LIKE ?;',
                                       (username, password)).fetchall()) > 0

    def set_online(self, username):
        """
        Sets a users status to be online
        :para m username:
        :return:
        """
        self.cursor.execute("UPDATE user SET online = 1 WHERE username LIKE ?;",
                            (username,))
        self.connection.commit()

    def set_offline(self, username=False, all=False):
        """
        Sets a users status to be online
        :param username:
        :param all:
        :return:
        """
        if all:
            self.cursor.execute("UPDATE user SET online = 0;")
        elif username:
            self.cursor.execute("UPDATE user SET online = 0 WHERE username LIKE ?;",
                            (username,))
        self.connection.commit()

