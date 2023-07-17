from flask_login import UserMixin
import sqlite3


class ConnectionToDB:
    def __init__(self, connection_to_db):
        self._connection = connection_to_db
        self._cursor = connection_to_db.cursor()

    def get_first_record(self, table, column, checked_value):
        """
        Get the first record from the table by selection with filtering by one field.
        """

        try:
            select_query = f"SELECT * FROM {table} " \
            f"WHERE {column} = {repr(checked_value)} " \
            f"LIMIT 1;"

            searched_record = self._cursor.execute(select_query).fetchone()
            return dict(searched_record) if searched_record is not None else False

        except sqlite3.Error as error:
            raise ValueError(("Error getting record from database", str(error)))

    def add_new_user(self, username, hash_sum_of_password):
        """
        Add new user to user table.
        """

        try:
            insert_query = f"INSERT INTO users (password, username) " \
            f"VALUES ({repr(hash_sum_of_password)}, {repr(username)});"

            self._cursor.execute(insert_query)
            self._connection.commit()

            new_user = self.get_first_record("users", "username", username)
            return new_user

        except sqlite3.Error as error:
            raise ValueError(("Error adding user to database", str(error)))

    def close(self):
        self._connection.close()


class UserLogin(UserMixin):
    def __init__(self, user_id=None, connection_to_db=None, user=None):
        if type(user_id) is str and user_id.isdigit() and connection_to_db is not None:
            self._user = connection_to_db.get_first_record("users", "id", user_id)
        elif type(user) is dict:
            self._user = user
        else:
            self._user = False

    def get_id(self):
        return str(self._user["id"])

    @property
    def username(self):
        return str(self._user["username"])