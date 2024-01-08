import unittest
import sqlite3
import bcrypt
from DB import create_table, insert_user  # Import the functions to test

class TestUserRegistration(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for testing
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        create_table()  # Create the table in the temporary database

    def tearDown(self):
        # Close the database connection after each test
        self.conn.close()

    def test_create_table(self):
        """Test if the table is created successfully."""
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='userdata'")
        result = self.cur.fetchone()
        self.assertEqual(result, 'userdata')

    def test_insert_user(self):
        """Test if user data is inserted correctly with password hashing."""
        username = "mazen123"
        password = "12345"
        insert_user(username, password)

        self.cur.execute("SELECT None, password, password_salt ")
        result = self.cur.fetchone()
        self.assertEqual(result, (username, bcrypt.hashpw(password.encode("utf-8"), result[2]), result[2]))

if __name__ == "__main__":
    unittest.main()
