from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in system"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)

    email = db.Column(db.Text, nullable = False, unique = True)

    username = db.Column(db.Text, nullable = False, unique = True)

    password = db.Column(db.Text, nullable = False)

    # add below back in when I've made a recipe class
    # saves = db.relationship('Recipe', secondary = 'saves')

    @classmethod
    def signup(cls, username, email, password):
        """sign up a user, hash their password, add them to the system"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username = username, email = email, password = hashed_pwd)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """find user with matching username and password. returns user object if it finds a user whose username and password hash match what's entered, if it can't find the user or password, it returns False."""

        user = cls.query.filter_by(username=username).first()
        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False

class Saves(db.Model):
    """connect user saves to recipes"""
    __tablename__ = 'saves'

    id = db.Column(db.Integer, primary_key = True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    recipe_id = db.Column(db.Integer, nullable = False)

# not sure how to make class Recipes since it should get its id 