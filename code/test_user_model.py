"""user model tests"""

# python3 -m unittest test_user_model.py in terminal

import os 
from unittest import TestCase
from models import db, User, Saves
# from bs4 import BeautifulSoup


os.environ['DATABASE_URL'] = "postgresql:///perfect-recipe-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """tests for user"""

    def setUp(self):
        """create test user"""

        User.query.delete()

        db.drop_all()
        db.create_all()

        testuser1 = User.signup('testuser1', 'testuser1@gmail.com', 'pwdpwdpwd')
        testuser1ID = 111111
        testuser1.id = testuser1ID

        testuser2 = User.signup('testuser2', 'testuser2@gmail.com', 'passwordhi')
        testuser2ID = 222222
        testuser2.id = testuser2ID

        db.session.commit()

        testuser1 = User.query.get(testuser1ID)
        testuser2 = User.query.get(testuser2ID)

        self.testuser1 = testuser1
        self.testuser1ID = testuser1ID

        self.testuser2 = testuser2
        self.testuser2ID = testuser2ID

        self.client = app.test_client()
    
    def tearDown(self):
        res = super(UserModelTestCase, self).tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """does the basic model work?"""

        u = User(
            email = "test@test.com", 
            username = "testuser",
            password = "hashed_password"
        )

        db.session.add(u)
        db.session.commit()

        # new user should have nothing saved
        self.assertEqual(len(u.saves), 0)

    # TEST SAVE METHOD HERE (REFER TO WARBLER PROJECT)

    def test_valid_signup(self):
        """test that signup works with valid credentials"""

        u_test = User.signup("testtesttest", "test@gmail.com", "password")
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "test@gmail.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """test that it catches an invalid username"""
        invalid = User.signup(None, "test@gmail.com", "password")
        uid = 23462432
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """test that it catches invalid email"""
        invalid = User.signup("testtest", None, "password")
        uid = 23423523
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """test that it catches an invalid password"""

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "test@gmail.com", "")
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "test@gmail.com", None)

    def test_valid_authentication(self):
        """test it authenticates correct credentials"""
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        """test catching invalid username"""
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        """test catching invalid password"""
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))