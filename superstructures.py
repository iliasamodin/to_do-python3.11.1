from flask_login import UserMixin
import sqlite3


class ConnectionToDB:
    def __init__(self, connection_to_db):
        self._connection = connection_to_db
        self._cursor = connection_to_db.cursor()

    def get_first_record(self, table, **kwargs):
        """
        Get the first record from the table.
        """

        list_of_values_for_columns = [f'{column} = {repr(value)}' for column, value in kwargs.items()]
        values_for_where = " AND ".join(list_of_values_for_columns)

        select_query = f"SELECT * FROM {table} " \
        f"{'WHERE ' if values_for_where else ''}{values_for_where} " \
        f"LIMIT 1;"

        searched_record = self._cursor.execute(select_query).fetchone()
        return searched_record

    def add_new_user(self, username, hash_sum_of_password):
        """
        Add new user to user table.
        """

        insert_query = f"INSERT INTO users (password, username) " \
        f"VALUES ({repr(hash_sum_of_password)}, {repr(username)});"

        self._cursor.execute(insert_query)
        self._connection.commit()

        new_user = self.get_first_record("users", username=username)
        return new_user

    def add_new_task(self, user_id, form_data):
        """
        Add new task to task table.
        """

        insert_query = "INSERT INTO tasks (" \
        "user_id, title, description, date_of_completion, time_of_completion, priority" \
        ") " \
        "VALUES ({user_id}, '{title}', '{description}', " \
        "'{date_of_completion}', '{time_of_completion}', {priority});".format(
            user_id=user_id, 
            **form_data
        )

        self._cursor.execute(insert_query)
        self._connection.commit()

    def get_tasks_for_user(self, user_id, filters=None, order_by=None):
        """
        Select user tasks filtered according to filters attribute and sorted according to order_by.
        """

        select_query = f"SELECT * FROM tasks " \
        f"WHERE user_id = {user_id}{f' AND {filters}' if filters is not None else ''}" \
        f"{f' ORDER BY {order_by}' if order_by is not None else ''};"

        tasks_for_user = self._cursor.execute(select_query).fetchall()
        return tasks_for_user if tasks_for_user is not None else False

    def update_task(self, task_id, **kvargs):
        """
        Update task data in the database.
        """

        list_of_new_values_for_columns = [f'{column} = {repr(value)}' for column, value in kvargs.items()]
        set_values = ", ".join(list_of_new_values_for_columns)
        if set_values:
            update_query = f"UPDATE tasks SET {set_values} " \
            f"WHERE id = {task_id};"

            self._cursor.execute(update_query)
            self._connection.commit()

    def close(self):
        self._connection.close()


class UserLogin(UserMixin):
    def __init__(self, user_id=None, connection_to_db=None, user=None):
        if type(user_id) is str and user_id.isdigit() and connection_to_db is not None:
            self._user = connection_to_db.get_first_record("users", id=user_id)
        elif type(user) is sqlite3.Row:
            self._user = user
        else:
            self._user = False

    def get_id(self):
        return str(self._user["id"])

    @property
    def username(self):
        return str(self._user["username"])