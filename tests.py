from to_do import db_connection
from superstructures import ConnectionToDB
import unittest


class TestConnectionToDB(unittest.TestCase):
    def setUp(self):
        self.connection_to_db = ConnectionToDB(db_connection())

    def test_get_first_record(self):
        self.assertEqual(self.connection_to_db.get_first_record("users", "id", "1")["username"], "demo")

    def test_get_missing_record(self):
        self.assertEqual(self.connection_to_db.get_first_record("users", "id", "0"), False)

    def test_get_record_from_non_existent_table(self):
        with self.assertRaises(ValueError) as error:
            self.connection_to_db.get_first_record("programmers", "id", "1")
            self.assertEqual(error.exception.args[0][0], "Error getting record from database")

    def test_add_existing_user(self):
        with self.assertRaises(ValueError) as error:
            self.connection_to_db.add_new_user("demo", "conditional_password")
            self.assertEqual(error.exception.args[0][0], "Error adding user to database")


if __name__ == "__main__":
    unittest.main()