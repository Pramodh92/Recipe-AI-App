from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is defined
from models.user import User, UserSession
from models.database import Recipe, SavedRecipe, Rating, MealPlan, ShoppingList