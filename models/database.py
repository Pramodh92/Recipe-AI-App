from datetime import datetime
from models import db

# User model is defined in models/user.py

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cuisine = db.Column(db.String(50))
    cooking_time = db.Column(db.Integer)  # in minutes
    difficulty = db.Column(db.String(20))
    servings = db.Column(db.Integer)
    flavor_profile = db.Column(db.Text)  # JSON string
    
    # Recipe source and generation info
    source_type = db.Column(db.String(20), default='ai_generated')  # ai_generated, manual, imported
    ai_model_used = db.Column(db.String(50), nullable=True)  # Which AI model generated this
    generation_prompt = db.Column(db.Text, nullable=True)  # Original user prompt
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    saved_by = db.relationship('SavedRecipe', backref='recipe', lazy=True)
    ratings = db.relationship('Rating', backref='recipe', lazy=True)
    
    @property
    def average_rating(self):
        if self.ratings:
            return sum(rating.rating for rating in self.ratings) / len(self.ratings)
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'cuisine': self.cuisine,
            'cooking_time': self.cooking_time,
            'difficulty': self.difficulty,
            'servings': self.servings,
            'flavor_profile': self.flavor_profile,
            'source_type': self.source_type,
            'ai_model_used': self.ai_model_used,
            'generation_prompt': self.generation_prompt,
            'created_by_user_id': self.created_by_user_id,
            'average_rating': self.average_rating,
            'created_at': self.created_at.isoformat()
        }

class SavedRecipe(db.Model):
    __tablename__ = 'saved_recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='_user_recipe_uc'),)

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='_user_recipe_rating_uc'),)

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    plan_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'items': self.items,
            'created_at': self.created_at.isoformat()
        }
