from to_do import db_connection
from superstructures import ConnectionToDB
import unittest, sqlite3


class TestConnectionToDB(unittest.TestCase):
    def setUp(self):
        self.connection_to_db = ConnectionToDB(db_connection())

    def test_get_first_record(self):
        self.assertEqual(self.connection_to_db.get_first_record("users", "id", "1")["username"], "demo")

    def test_get_missing_record(self):
        self.assertEqual(self.connection_to_db.get_first_record("users", "id", "0"), False)

    def test_get_record_from_non_existent_table(self):
        self.assertRaises(sqlite3.OperationalError, self.connection_to_db.get_first_record, 
            "programmers", "id", "1"
        )

    def test_add_existing_user(self):
        self.assertRaises(sqlite3.IntegrityError, self.connection_to_db.add_new_user, 
            "demo", "conditional_password"
        )

    def test_get_tasks_for_user(self):
        self.assertEqual(dict(list(self.connection_to_db.get_tasks_for_user("1"))[0])["title"], "First task")

    def test_get_tasks_with_filtering_by_non_existent_field(self):
        self.assertRaises(sqlite3.OperationalError, self.connection_to_db.get_tasks_for_user, 
            "1", filters="datetime_of_completion = 2023-07-18 16:00"
        )

    def test_get_tasks_with_ordering_by_non_existent_field(self):
        self.assertRaises(sqlite3.OperationalError, self.connection_to_db.get_tasks_for_user, 
            "1", order_by="datetime_of_completion"
        )

    def test_update_task_with_updating_non_existent_field(self):
        self.assertRaises(sqlite3.OperationalError, self.connection_to_db.update_task, 
            "1", datetime_of_completion="2023-07-18 16:00"
        )


if __name__ == "__main__":
    unittest.main()