"""user model tests"""

# python3 -m unittest test_user_model.py in terminal

import os 
from unittest import TestCase
from models import db, User, Saves
from sqlalchemy.exc import IntegrityError


os.environ['DATABASE_URL'] = "postgresql:///perfect-recipe-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """tests for user"""

    def setUp(self):
        """create test user"""

        db.drop_all()
        db.create_all()

        testuser1 = User.signup('testuser1', 'testuser1@gmail.com', 'pwdpwdpwd')
        testuser1ID = 111111
        testuser1.id = testuser1ID

        db.session.commit()

        testuser1 = User.query.get(testuser1ID)

        self.testuser1 = testuser1
        self.testuser1ID = testuser1ID

        self.client = app.test_client()
    
    def tearDown(self):
        res = super(UserModelTestCase, self).tearDown()
        db.session.rollback()
        return res

    # def setup_saves(self):
    #     """add a saved recipe for test user"""
    #     new_save = Saves(user_id = self.testuser1ID, recipe_id = 655447)
    #     db.session.add(new_save)
    #     db.session.commit()


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

    def test_adding_save(self):
        """test that adding a save shows up"""

        u = User(
            email = "testtest@test.com", 
            username = "testuserhello",
            password = "hashed_password"
        )

        db.session.add(u)
        db.session.commit()
        
        new_user_save = Saves(user_id = u.id, recipe_id = 655447)

        db.session.add(new_user_save)
        db.session.commit()

        self.assertEqual(len(u.saves), 1)

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
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """test that it catches invalid email"""
        invalid = User.signup("testtest", None, "password")
        uid = 23423523
        invalid.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """test that it catches an invalid password"""

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "test@gmail.com", "")
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "test@gmail.com", None)

    def test_valid_authentication(self):
        """test it authenticates correct credentials"""
        u = User.authenticate(self.testuser1.username, "pwdpwdpwd")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.testuser1ID)

    def test_invalid_username(self):
        """test catching invalid username"""
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        """test catching invalid password"""
        self.assertFalse(User.authenticate(self.testuser1.username, "badpassword"))

    def test_show_user_saves(self):
        """test catching unlogged in user attempting to see saves and redirect them to log in"""
        
        with self.client as c:
            resp = c.get(f"/user/{self.testuser1ID}/saves", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('please log in to see your likes', str(resp.data))
            self.assertIn('<h2 class="join-message">welcome back, ', str(resp.data))

    def test_home_page(self):
        """test that it loads the correct home page"""

        with self.client as c:
            resp = c.get(f"/", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<h2>welcome to the perfect recipe generator</h2>', str(resp.data))

    def test_search_form(self):
        """test the search form"""
        with self.client as c:
            resp = c.get("/recipe/search")

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<h6>all categories are optional--if you enter nothing, you will be shown random recipes</h6>', str(resp.data))

    def test_recipe_details(self):
        """test the recipe details page is loading and communicating with the API"""
        with self.client as c:
            resp = c.get(f"/recipe/655447", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<h4>try out some similar recipes:</h4>', str(resp.data))
            self.assertIn('Pear, Goat Cheese and Spinach Salad with Warm Maple-Bacon Dressing', str(resp.data))
            self.assertIn('baby spinach', str(resp.data))

    def test_show_random_recipes(self):
        """test that the show search results page loads and shows random recipes if nothing entered"""
        with self.client as c:
            resp = c.get(f"/recipe/search/results?need_to_have=&can_not_have=&max_time=&intolerances=&diet=&cuisine=&type_food=", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<h2>here are your recipes!</h2>', str(resp.data))
 
    def test_show_search_results(self):
        """test that the show search results page loads and shows recipes when there are parameters"""
        with self.client as c:
            resp = c.get(f"/recipe/search/results?need_to_have=pears&can_not_have=&max_time=&intolerances=&diet=&cuisine=&type_food=", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('<h2>here are your recipes!</h2>', str(resp.data))

    def test_show_search_results(self):
        """test that the show search results page loads and shows error message when nothing matches"""
        with self.client as c:
            resp = c.get(f"/recipe/search/results?need_to_have=pears%2C+cream%2C+oats%2C+beef&can_not_have=&max_time=&intolerances=&diet=&cuisine=&type_food=", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("<h2>hm, it looks like your search didn", str(resp.data))



        
