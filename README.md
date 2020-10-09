# perfect-recipe-capstone
url: https://perfect-recipe.herokuapp.com/

This website is built to save time when deciding what to cook. It allows users to search recipes by a variety of terms based on ingredients they have available, time they have to cook, dietary restrictions, and more. 

Logged in users can save recipes to come back to later. The site also will recommend similar recipes based on the recipe the user is currently viewing. 
Users who are not logged in can not save recipes, but they can still use the search capabilities and see similar recipe recommendations.

On the home page, the user is shown randomly generated recipes. All search inputs are optional, and if a user enters nothing they will be shown random recipes.
The only input error that will stop the user from being redirected to a recipe results page is a syntax error in the need-to-have ingredients input, as it is the most important input. I chose not to stop users from seeing recipes when they input something nonsensical in another field because there are a lot of search fields and I thought the user flow might be somewhat frustrating if they are constantly getting stopped from seeing recipes due to typos in input fields.

I used the spoonacular API: https://spoonacular.com/food-api

This site is built primarily using Python with Flask, and tested through Python as well. I also used Jinja, WTForms, SQLAlchemy, Postgres, Javascript, HTML, CSS and Bootstrap. It is deployed through Heroku.

