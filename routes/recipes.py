from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models.database import db, Recipe, SavedRecipe, Rating
from models.user import User
from services.ai_client import ai_client
import json
import logging

recipes_bp = Blueprint('recipes', __name__)
logger = logging.getLogger(__name__)

@recipes_bp.route('/generator')
def generator_page():
    return render_template('recipes/generator.html')

@recipes_bp.route('/generate', methods=['POST'])
async def generate_recipe():
    try:
        # Optional authentication check
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        data = request.get_json() if request.is_json else request.form
        
        ingredients = data.get('ingredients', '').strip()
        dietary_restrictions = data.get('dietary_restrictions', '')
        cuisine = data.get('cuisine', '')
        servings = int(data.get('servings', 4))
        
        # Get user's preferred language
        language = 'en'
        if user_id:
            user = User.query.get(user_id)
            if user:
                language = user.preferred_language
        
        if not ingredients:
            return jsonify({'success': False, 'message': 'Ingredients are required'}), 400
        
        # Generate recipe using AI
        result = await ai_client.generate_recipe(
            ingredients=ingredients,
            dietary_restrictions=dietary_restrictions,
            cuisine=cuisine,
            servings=servings,
            language=language
        )
        
        if not result['success']:
            return jsonify({'success': False, 'message': 'Recipe generation failed'}), 500
        
        recipe_data = result['data']
        
        # Save recipe to database with metadata for meal planning and shopping list integration
        recipe = Recipe(
            title=recipe_data['title'],
            ingredients=json.dumps(recipe_data['ingredients']),
            instructions=json.dumps(recipe_data['instructions']),
            cuisine=recipe_data.get('cuisine'),
            cooking_time=recipe_data.get('cooking_time'),
            difficulty=recipe_data.get('difficulty'),
            servings=recipe_data.get('servings'),
            flavor_profile=json.dumps(recipe_data.get('flavor_profile', {})),
            source_type='ai_generated',
            ai_model_used='Gemini',
            generation_prompt=f"Ingredients: {ingredients}, Dietary: {dietary_restrictions}, Cuisine: {cuisine}",
            created_by_user_id=user_id
        )
        
        db.session.add(recipe)
        db.session.commit()
        
        # Add recipe ID to response
        recipe_response = recipe_data.copy()
        recipe_response['id'] = recipe.id
        
        logger.info(f"Generated recipe: {recipe_data['title']} (ID: {recipe.id})")
        
        return jsonify({
            'success': True,
            'recipe': recipe_response
        })
        
    except Exception as e:
        logger.error(f"Recipe generation error: {str(e)}")
        return jsonify({'success': False, 'message': 'Recipe generation failed'}), 500

@recipes_bp.route('/create', methods=['POST'])
@jwt_required()
def create_recipe():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'Recipe data required'}), 400
        
        # Create new recipe from data
        recipe = Recipe(
            title=data.get('title'),
            ingredients=json.dumps(data.get('ingredients', [])),
            instructions=json.dumps(data.get('instructions', [])),
            cuisine=data.get('cuisine'),
            cooking_time=data.get('cooking_time'),
            difficulty=data.get('difficulty'),
            servings=data.get('servings'),
            flavor_profile=json.dumps(data.get('flavor_profile', {})),
            created_by_user_id=user_id
        )
        
        db.session.add(recipe)
        db.session.commit()
        
        # Save recipe to user's saved recipes
        saved_recipe = SavedRecipe(user_id=user_id, recipe_id=recipe.id)
        db.session.add(saved_recipe)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Recipe created and saved successfully',
            'recipe_id': recipe.id
        })
        
    except Exception as e:
        logger.error(f"Create recipe error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to create recipe'}), 500

@recipes_bp.route('/save', methods=['POST'])
@jwt_required()
def save_recipe():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        recipe_id = data.get('recipe_id')
        
        if not recipe_id:
            return jsonify({'success': False, 'message': 'Recipe ID required'}), 400
        
        # Check if recipe exists
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found'}), 404
        
        # Check if already saved
        existing = SavedRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Recipe already saved'}), 400
        
        # Save recipe
        saved_recipe = SavedRecipe(user_id=user_id, recipe_id=recipe_id)
        db.session.add(saved_recipe)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Recipe saved successfully'})
        
    except Exception as e:
        logger.error(f"Save recipe error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to save recipe'}), 500

@recipes_bp.route('/unsave', methods=['POST'])
@jwt_required()
def unsave_recipe():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        recipe_id = data.get('recipe_id')
        
        if not recipe_id:
            return jsonify({'success': False, 'message': 'Recipe ID required'}), 400
        
        # Check if recipe exists and is saved by the user
        saved_recipe = SavedRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        if not saved_recipe:
            return jsonify({'success': False, 'message': 'Recipe not found in your saved recipes'}), 404
        
        # Remove from saved recipes
        db.session.delete(saved_recipe)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Recipe removed from saved recipes'})
        
    except Exception as e:
        logger.error(f"Unsave recipe error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to remove recipe from saved recipes'}), 500

@recipes_bp.route('/saved')
@jwt_required()
def get_saved_recipes():
    try:
        user_id = get_jwt_identity()
        
        saved_recipes = db.session.query(Recipe).join(SavedRecipe).filter(
            SavedRecipe.user_id == user_id
        ).all()
        
        recipes_data = []
        for recipe in saved_recipes:
            recipe_dict = recipe.to_dict()
            # Parse JSON fields
            recipe_dict['ingredients'] = json.loads(recipe.ingredients)
            recipe_dict['instructions'] = json.loads(recipe.instructions)
            if recipe.flavor_profile:
                recipe_dict['flavor_profile'] = json.loads(recipe.flavor_profile)
            recipes_data.append(recipe_dict)
        
        if request.is_json:
            return jsonify({'success': True, 'recipes': recipes_data})
        else:
            return render_template('recipes/saved.html', recipes=recipes_data)
        
    except Exception as e:
        logger.error(f"Get saved recipes error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch saved recipes'}), 500

@recipes_bp.route('/rate', methods=['POST'])
@jwt_required()
def rate_recipe():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        recipe_id = data.get('recipe_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not recipe_id or rating is None:
            return jsonify({'success': False, 'message': 'Recipe ID and rating required'}), 400
        
        if not (1 <= rating <= 5):
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
        
        # Check if recipe exists
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found'}), 404
        
        # Update or create rating
        existing_rating = Rating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        
        if existing_rating:
            existing_rating.rating = rating
            existing_rating.comment = comment
        else:
            new_rating = Rating(
                user_id=user_id,
                recipe_id=recipe_id,
                rating=rating,
                comment=comment
            )
            db.session.add(new_rating)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Rating submitted successfully'})
        
    except Exception as e:
        logger.error(f"Rate recipe error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to submit rating'}), 500

@recipes_bp.route('/<int:recipe_id>')
def get_recipe(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found'}), 404
        
        recipe_dict = recipe.to_dict()
        # Parse JSON fields
        recipe_dict['ingredients'] = json.loads(recipe.ingredients)
        recipe_dict['instructions'] = json.loads(recipe.instructions)
        if recipe.flavor_profile:
            recipe_dict['flavor_profile'] = json.loads(recipe.flavor_profile)
        
        return jsonify({'success': True, 'recipe': recipe_dict})
        
    except Exception as e:
        logger.error(f"Get recipe error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch recipe'}), 500
