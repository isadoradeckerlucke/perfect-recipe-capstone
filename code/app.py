import os
from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
import requests
import json
from flask_cors import CORS
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Saves
from forms import LoginForm, AddUserForm
from secrets import api_key_1, api_key_2, api_key_3
# don't forget to run seed.py!!!

CURR_USER_KEY = 'current_user'
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///perfect-recipe'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


connect_db(app)

# API calls I'll need to make
# GET recipes by ingredients, GET recipe IDs, GET recipe info by ID, 

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def check_if_saved(recipe_id):
    """check if a recipe has been saved by the user. returns True if recipe has already been saved, False if not"""
    
    user_saves = g.user.saves
    # create a list of the saved recipe ids so that i can tell whether to add to saves or remove from saves
    num_saves = len(user_saves)
    id_list = []

    for i in range(num_saves):
        saved_recipe_id = g.user.saves[i].recipe_id
        id_list.append(saved_recipe_id)

    if recipe_id in id_list:
        return True
    else:
        return False


@app.route('/')
def home_page():
    """welcome user and show them recipes"""
    # could be random recipes or sorted by food type

    random_recipes = requests.get(f"https://api.spoonacular.com/recipes/random?apiKey={api_key_1}&number=12").json()
    print(random_recipes)

    saved_var_array = []
    for recipe in random_recipes['recipes']:
        saved_var_array.append(check_if_saved(recipe['id']))


    return render_template('home.html', random_recipes = random_recipes, saved_var_array = saved_var_array)

@app.route('/signup', methods = ["GET", "POST"])
def signup():
    """sign up a new user, add to db, redirect home. if a user with that name already exists, flash message, show form again"""

    form = AddUserForm()

    if form.validate_on_submit():
        try: 
            user = User.signup(
                username = form.username.data,
                password = form.password.data,
                email = form.email.data,
            )
            db.session.commit()
        except IntegrityError:
            flash('sorry, this username is already taken!', 'danger')
            return render_template('signup.html', form = form)

        do_login(user)
        return redirect('/')

    else:
        return render_template('signup.html', form = form)

@app.route('/logout')
def logout():
    """log user out"""
    do_logout()
    flash("you've been logged out. let's cook again soon!")
    return redirect('/')

@app.route('/login', methods = ["GET", "POST"])
def login():
    """log existing user in"""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            # flash(f"hey {user.username}, let's cook!")
            return redirect('/')

        flash("sorry, we don't recognize that username/password combo", "warning")

    return render_template('login.html', form = form)

@app.route('/recipe/search')
def search_recipes():
    """display search form"""
    return render_template('search.html')

@app.route('/recipe/search/results')
def display_search_results():
    """display results of user search"""
    need_to_have = request.args['need_to_have']
    max_time = request.args['max_time']
    can_not_have = request.args['can_not_have']
    intolerances = request.args['intolerances']
    diet = request.args['diet']
    cuisine = request.args['cuisine']
    type_food = request.args['type_food']

    base_url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={api_key_1}&number=21&instructionsRequired=true"

    if need_to_have: 
        base_url += f"&includeIngredients={need_to_have}"
    if max_time:
        base_url += f"&maxReadyTime={max_time}"
    if can_not_have:
        base_url += f"&excludeIngredients={can_not_have}"
    if intolerances:
        base_url += f"&intolerances={intolerances}"
    if diet:
        base_url += f"&diet={diet}"
    if cuisine:
        base_url += f"&cuisine={cuisine}"
    if type_food:
        base_url += f"&type={type_food}"

    recipes = requests.get(base_url).json()

    saved_var_array = []
    for recipe in recipes['results']:
        saved_var_array.append(check_if_saved(recipe['id']))


    return render_template('search_results.html', recipes = recipes, saved_var_array=saved_var_array)


@app.route('/recipe/<int:recipe_id>')
def show_recipe_details(recipe_id):
    """show details on a specific recipe"""
    recipe = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key_1}").json()

    if recipe['instructions']:
        instructions = ""
        soup_instructions = BeautifulSoup(recipe['instructions'], 'html.parser')
        for string in soup_instructions.stripped_strings:
            stripped_instructions = string.replace('\n', ' ')

            instructions += stripped_instructions
    else:
        instructions = "we couldn't find instructions for this recipe :("

    similar_recipes = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/similar?apiKey={api_key_1}&number=3").json()

    saved_var_main = check_if_saved(recipe_id)
    saved_var_array_similar = []
    for similar_recipe in similar_recipes:
        saved_var_array_similar.append(check_if_saved(similar_recipe['id']))


    return render_template('recipe_details.html', saved_var_main = saved_var_main, recipe = recipe, instructions = instructions, similar_recipes = similar_recipes, saved_var_array_similar = saved_var_array_similar)

###############################################################################
"""save routes"""

@app.route('/user/<int:user_id>/saves', methods = ["GET"])
def show_user_saves(user_id):
    """show recipes a user has saved"""
    if not g.user:
        flash("please log in to see your likes")
        return redirect('/login')

    user = User.query.get_or_404(user_id)
    
    saves_list = []

    num_saves = len(user.saves)
    for i in range(num_saves):
        recipe_id = user.saves[i].recipe_id
        saved_recipe = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key_1}").json()
        saves_list.append(saved_recipe)

    return render_template('saves.html', user = user, saves_list = saves_list)

@app.route('/recipe/<int:recipe_id>/save', methods = ['POST'])
def save_recipe(recipe_id):
    """if you are logged in, save a recipe"""

    if not g.user: 
        flash('you must be logged in to save a recipe')

    user_saves = g.user.saves
    # create a list of the saved recipe ids so that i can tell whether to add to saves or remove from saves
    num_saves = len(user_saves)
    id_list = []

    for i in range(num_saves):
        saved_recipe_id = g.user.saves[i].recipe_id
        id_list.append(saved_recipe_id)

    if check_if_saved(recipe_id) == True:
        index_recipe_id = id_list.index(recipe_id)
        del g.user.saves[index_recipe_id]
    else:
        new_save = Saves(user_id = g.user.id, recipe_id = recipe_id)
        db.session.add(new_save)

    db.session.commit()

    return redirect(f"/")

        

