from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from sqlalchemy import func, text
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

class Recipe(db.Model):
    """Recipe model for storing AI-generated and user recipes"""
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=False)  # JSON string
    instructions = db.Column(db.Text, nullable=False)  # JSON string
    
    # Recipe metadata
    cuisine = db.Column(db.String(50), nullable=True, index=True)
    cooking_time = db.Column(db.Integer, nullable=True, index=True)  # in minutes
    prep_time = db.Column(db.Integer, nullable=True)  # in minutes
    difficulty = db.Column(db.String(20), nullable=True, index=True)  # Easy, Medium, Hard
    servings = db.Column(db.Integer, default=4)
    
    # Nutritional information (optional)
    calories_per_serving = db.Column(db.Integer, nullable=True)
    protein_grams = db.Column(db.Float, nullable=True)
    carbs_grams = db.Column(db.Float, nullable=True)
    fat_grams = db.Column(db.Float, nullable=True)
    fiber_grams = db.Column(db.Float, nullable=True)
    
    # Flavor profile and tags
    flavor_profile = db.Column(db.Text, nullable=True)  # JSON string
    recipe_tags = db.Column(db.Text, nullable=True)  # JSON string (e.g., ["vegetarian", "quick", "healthy"])
    
    # Recipe source and generation info
    source_type = db.Column(db.String(20), default='ai_generated')  # ai_generated, manual, imported
    ai_model_used = db.Column(db.String(50), nullable=True)  # Which AI model generated this
    generation_prompt = db.Column(db.Text, nullable=True)  # Original user prompt
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Recipe status and visibility
    is_public = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)  # Verified by culinary experts
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    
    # Recipe image and media
    image_url = db.Column(db.String(512), nullable=True)
    video_url = db.Column(db.String(512), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    saved_by = db.relationship('SavedRecipe', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    recipe_variations = db.relationship('RecipeVariation', backref='original_recipe', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title, ingredients, instructions, **kwargs):
        self.title = title
        self.set_ingredients(ingredients if isinstance(ingredients, list) else [ingredients])
        self.set_instructions(instructions if isinstance(instructions, list) else [instructions])
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_ingredients(self, ingredients_list):
        """Set ingredients as JSON"""
        if isinstance(ingredients_list, list):
            self.ingredients = json.dumps(ingredients_list)
        else:
            self.ingredients = json.dumps([str(ingredients_list)])
    
    def get_ingredients(self):
        """Get ingredients as list"""
        if self.ingredients:
            try:
                return json.loads(self.ingredients)
            except json.JSONDecodeError:
                return [self.ingredients]
        return []
    
    def set_instructions(self, instructions_list):
        """Set instructions as JSON"""
        if isinstance(instructions_list, list):
            self.instructions = json.dumps(instructions_list)
        else:
            self.instructions = json.dumps([str(instructions_list)])
    
    def get_instructions(self):
        """Get instructions as list"""
        if self.instructions:
            try:
                return json.loads(self.instructions)
            except json.JSONDecodeError:
                return [self.instructions]
        return []
    
    def set_flavor_profile(self, flavor_dict):
        """Set flavor profile as JSON"""
        if flavor_dict and isinstance(flavor_dict, dict):
            self.flavor_profile = json.dumps(flavor_dict)
        else:
            self.flavor_profile = None
    
    def get_flavor_profile(self):
        """Get flavor profile as dict"""
        if self.flavor_profile:
            try:
                return json.loads(self.flavor_profile)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_tags(self, tags_list):
        """Set recipe tags as JSON"""
        if tags_list and isinstance(tags_list, list):
            self.recipe_tags = json.dumps(tags_list)
        else:
            self.recipe_tags = None
    
    def get_tags(self):
        """Get recipe tags as list"""
        if self.recipe_tags:
            try:
                return json.loads(self.recipe_tags)
            except json.JSONDecodeError:
                return []
        return []
    
    @hybrid_property
    def total_time(self):
        """Calculate total cooking time"""
        total = 0
        if self.prep_time:
            total += self.prep_time
        if self.cooking_time:
            total += self.cooking_time
        return total if total > 0 else self.cooking_time
    
    @hybrid_property
    def average_rating(self):
        """Get average rating for this recipe"""
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0.0
    
    @hybrid_property
    def rating_count(self):
        """Get total number of ratings"""
        return self.ratings.count()
    
    @hybrid_property
    def save_count(self):
        """Get number of times recipe has been saved"""
        return self.saved_by.count()
    
    def get_difficulty_level(self):
        """Get difficulty as integer (1-5)"""
        difficulty_map = {
            'easy': 1,
            'medium': 3,
            'hard': 5
        }
        return difficulty_map.get(self.difficulty.lower() if self.difficulty else 'medium', 3)
    
    def get_nutrition_info(self):
        """Get nutritional information as dict"""
        return {
            'calories_per_serving': self.calories_per_serving,
            'protein_grams': self.protein_grams,
            'carbs_grams': self.carbs_grams,
            'fat_grams': self.fat_grams,
            'fiber_grams': self.fiber_grams,
            'servings': self.servings
        }
    
    def calculate_total_nutrition(self):
        """Calculate total nutrition for all servings"""
        if not self.calories_per_serving:
            return None
        
        return {
            'total_calories': self.calories_per_serving * self.servings,
            'total_protein': (self.protein_grams or 0) * self.servings,
            'total_carbs': (self.carbs_grams or 0) * self.servings,
            'total_fat': (self.fat_grams or 0) * self.servings,
            'total_fiber': (self.fiber_grams or 0) * self.servings
        }
    
    def scale_recipe(self, new_servings):
        """Scale recipe ingredients for different serving size"""
        if not new_servings or new_servings <= 0:
            return None
        
        scale_factor = new_servings / self.servings
        scaled_ingredients = []
        
        for ingredient in self.get_ingredients():
            # Basic scaling - in production, implement more sophisticated ingredient parsing
            scaled_ingredients.append(f"{ingredient} (scaled for {new_servings} servings)")
        
        return {
            'title': f"{self.title} (Scaled for {new_servings} servings)",
            'ingredients': scaled_ingredients,
            'instructions': self.get_instructions(),
            'servings': new_servings,
            'cooking_time': self.cooking_time,
            'prep_time': self.prep_time,
            'difficulty': self.difficulty
        }
    
    def get_similar_recipes(self, limit=5):
        """Find similar recipes based on cuisine and ingredients"""
        if not self.cuisine:
            return []
        
        # Simple similarity based on cuisine and common ingredients
        similar = Recipe.query.filter(
            Recipe.id != self.id,
            Recipe.cuisine == self.cuisine,
            Recipe.is_public == True,
            Recipe.status == 'active'
        ).order_by(func.random()).limit(limit).all()
        
        return similar
    
    def get_recipe_complexity_score(self):
        """Calculate recipe complexity score (1-10)"""
        score = 1
        
        # Add points for number of ingredients
        ingredients_count = len(self.get_ingredients())
        score += min(ingredients_count // 3, 3)
        
        # Add points for number of steps
        steps_count = len(self.get_instructions())
        score += min(steps_count // 2, 3)
        
        # Add points for cooking time
        if self.cooking_time:
            if self.cooking_time > 60:
                score += 2
            elif self.cooking_time > 30:
                score += 1
        
        # Add points for difficulty
        if self.difficulty:
            if self.difficulty.lower() == 'hard':
                score += 2
            elif self.difficulty.lower() == 'medium':
                score += 1
        
        return min(score, 10)
    
    def is_suitable_for_diet(self, dietary_restrictions):
        """Check if recipe is suitable for given dietary restrictions"""
        if not dietary_restrictions:
            return True
        
        recipe_tags = self.get_tags()
        ingredients = [ing.lower() for ing in self.get_ingredients()]
        
        for restriction in dietary_restrictions:
            restriction = restriction.lower()
            
            if restriction == 'vegetarian':
                # Check for meat ingredients (basic implementation)
                meat_keywords = ['chicken', 'beef', 'pork', 'fish', 'lamb', 'turkey', 'bacon']
                if any(meat in ' '.join(ingredients) for meat in meat_keywords):
                    return False
            
            elif restriction == 'vegan':
                # Check for animal products (basic implementation)
                animal_keywords = ['milk', 'cheese', 'butter', 'egg', 'cream', 'yogurt', 'honey']
                if any(animal in ' '.join(ingredients) for animal in animal_keywords):
                    return False
            
            elif restriction == 'gluten-free':
                # Check for gluten-containing ingredients
                gluten_keywords = ['wheat', 'flour', 'bread', 'pasta', 'barley', 'rye']
                if any(gluten in ' '.join(ingredients) for gluten in gluten_keywords):
                    return False
        
        return True
    
    def get_shopping_list_items(self):
        """Extract shopping list items from ingredients"""
        ingredients = self.get_ingredients()
        shopping_items = []
        
        for ingredient in ingredients:
            # Basic ingredient processing - extract item name
            # In production, implement more sophisticated parsing
            cleaned_ingredient = ingredient.strip()
            shopping_items.append(cleaned_ingredient)
        
        return shopping_items
    
    def to_dict(self, include_detailed=False):
        """Convert recipe to dictionary for API responses"""
        recipe_dict = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'ingredients': self.get_ingredients(),
            'instructions': self.get_instructions(),
            'cuisine': self.cuisine,
            'cooking_time': self.cooking_time,
            'prep_time': self.prep_time,
            'total_time': self.total_time,
            'difficulty': self.difficulty,
            'servings': self.servings,
            'average_rating': round(self.average_rating, 1),
            'rating_count': self.rating_count,
            'save_count': self.save_count,
            'tags': self.get_tags(),
            'source_type': self.source_type,
            'is_featured': self.is_featured,
            'is_verified': self.is_verified,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }
        
        if include_detailed:
            recipe_dict.update({
                'flavor_profile': self.get_flavor_profile(),
                'nutrition_info': self.get_nutrition_info(),
                'complexity_score': self.get_recipe_complexity_score(),
                'ai_model_used': self.ai_model_used,
                'generation_prompt': self.generation_prompt,
                'video_url': self.video_url,
                'updated_at': self.updated_at.isoformat()
            })
        
        return recipe_dict
    
    def to_search_dict(self):
        """Convert recipe to dictionary optimized for search results"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'cuisine': self.cuisine,
            'cooking_time': self.cooking_time,
            'difficulty': self.difficulty,
            'servings': self.servings,
            'average_rating': round(self.average_rating, 1),
            'tags': self.get_tags(),
            'image_url': self.image_url,
            'ingredient_count': len(self.get_ingredients())
        }
    
    @staticmethod
    def search_recipes(query, filters=None, page=1, per_page=20):
        """Search recipes with filters and pagination"""
        recipes_query = Recipe.query.filter(
            Recipe.is_public == True,
            Recipe.status == 'active'
        )
        
        # Text search
        if query:
            search_filter = Recipe.title.contains(query) | Recipe.ingredients.contains(query)
            recipes_query = recipes_query.filter(search_filter)
        
        # Apply filters
        if filters:
            if filters.get('cuisine'):
                recipes_query = recipes_query.filter(Recipe.cuisine == filters['cuisine'])
            
            if filters.get('difficulty'):
                recipes_query = recipes_query.filter(Recipe.difficulty == filters['difficulty'])
            
            if filters.get('max_time'):
                recipes_query = recipes_query.filter(Recipe.cooking_time <= filters['max_time'])
            
            if filters.get('min_rating'):
                # This would need a subquery for average rating
                pass
        
        # Order by relevance/popularity
        recipes_query = recipes_query.order_by(Recipe.created_at.desc())
        
        # Paginate
        pagination = recipes_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'recipes': [recipe.to_search_dict() for recipe in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    def __repr__(self):
        return f'<Recipe {self.title}>'

class SavedRecipe(db.Model):
    """Track recipes saved by users"""
    __tablename__ = 'saved_recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)  # User's personal notes
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='_user_recipe_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recipe_id': self.recipe_id,
            'saved_at': self.saved_at.isoformat(),
            'notes': self.notes
        }

class Rating(db.Model):
    """Recipe ratings and reviews"""
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    would_make_again = db.Column(db.Boolean, nullable=True)
    difficulty_rating = db.Column(db.Integer, nullable=True)  # User's perception of difficulty
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Moderation fields
    is_verified = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='_user_recipe_rating_uc'),)
    
    def to_dict(self, include_user=False):
        rating_dict = {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'rating': self.rating,
            'comment': self.comment,
            'would_make_again': self.would_make_again,
            'difficulty_rating': self.difficulty_rating,
            'created_at': self.created_at.isoformat(),
            'is_verified': self.is_verified
        }
        
        if include_user and hasattr(self, 'user'):
            rating_dict['user'] = {
                'id': self.user.id,
                'name': self.user.name
            }
        
        return rating_dict

class RecipeVariation(db.Model):
    """Store recipe variations created by users"""
    __tablename__ = 'recipe_variations'
    
    id = db.Column(db.Integer, primary_key=True)
    original_recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    changes_made = db.Column(db.Text, nullable=False)  # JSON string describing changes
    ingredients = db.Column(db.Text, nullable=False)  # JSON string
    instructions = db.Column(db.Text, nullable=False)  # JSON string
    notes = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_changes(self, changes_dict):
        """Set changes as JSON"""
        if changes_dict:
            self.changes_made = json.dumps(changes_dict)
    
    def get_changes(self):
        """Get changes as dict"""
        if self.changes_made:
            try:
                return json.loads(self.changes_made)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_recipe_id': self.original_recipe_id,
            'title': self.title,
            'description': self.description,
            'changes_made': self.get_changes(),
            'notes': self.notes,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat()
        }

class MealPlan(db.Model):
    """Weekly meal plans"""
    __tablename__ = 'meal_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    week_start = db.Column(db.Date, nullable=False, index=True)
    plan_data = db.Column(db.Text, nullable=False)  # JSON string
    notes = db.Column(db.Text, nullable=True)
    is_template = db.Column(db.Boolean, default=False)  # Reusable template
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_plan_data(self, plan_dict):
        """Set meal plan data as JSON"""
        if plan_dict:
            self.plan_data = json.dumps(plan_dict)
    
    def get_plan_data(self):
        """Get meal plan data as dict"""
        if self.plan_data:
            try:
                return json.loads(self.plan_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_all_recipes(self):
        """Get all recipes used in this meal plan"""
        plan_data = self.get_plan_data()
        recipe_ids = set()
        
        for day_meals in plan_data.values():
            if isinstance(day_meals, dict):
                for meal_info in day_meals.values():
                    if isinstance(meal_info, dict) and 'id' in meal_info:
                        recipe_ids.add(meal_info['id'])
        
        return Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'week_start': self.week_start.isoformat(),
            'plan_data': self.get_plan_data(),
            'notes': self.notes,
            'is_template': self.is_template,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ShoppingList(db.Model):
    """Shopping lists generated from recipes"""
    __tablename__ = 'shopping_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string
    source_recipes = db.Column(db.Text, nullable=True)  # JSON array of recipe IDs
    is_completed = db.Column(db.Boolean, default=False)
    completed_items = db.Column(db.Text, nullable=True)  # JSON array of completed item indices
    estimated_cost = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_items(self, items_dict):
        """Set shopping list items as JSON"""
        if items_dict:
            self.items = json.dumps(items_dict)
    
    def get_items(self):
        """Get shopping list items as dict"""
        if self.items:
            try:
                return json.loads(self.items)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_source_recipes(self, recipe_ids):
        """Set source recipe IDs as JSON"""
        if recipe_ids:
            self.source_recipes = json.dumps(recipe_ids)
    
    def get_source_recipes(self):
        """Get source recipe IDs as list"""
        if self.source_recipes:
            try:
                return json.loads(self.source_recipes)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_completed_items(self, completed_indices):
        """Set completed item indices as JSON"""
        if completed_indices:
            self.completed_items = json.dumps(completed_indices)
    
    def get_completed_items(self):
        """Get completed item indices as list"""
        if self.completed_items:
            try:
                return json.loads(self.completed_items)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_total_items_count(self):
        """Get total number of items in shopping list"""
        items = self.get_items()
        if isinstance(items, dict) and 'categories' in items:
            total = 0
            for category_items in items['categories'].values():
                total += len(category_items)
            return total
        return 0
    
    def get_completion_percentage(self):
        """Get completion percentage"""
        total_items = self.get_total_items_count()
        if total_items == 0:
            return 0
        
        completed_count = len(self.get_completed_items())
        return round((completed_count / total_items) * 100, 1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'items': self.get_items(),
            'source_recipes': self.get_source_recipes(),
            'is_completed': self.is_completed,
            'completed_items': self.get_completed_items(),
            'estimated_cost': self.estimated_cost,
            'total_items_count': self.get_total_items_count(),
            'completion_percentage': self.get_completion_percentage(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
