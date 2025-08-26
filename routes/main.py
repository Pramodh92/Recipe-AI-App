from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.database import Recipe, MealPlan, db
from models.user import User
import json
from datetime import datetime, timedelta
import logging

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    try:
        # Get trending recipes (most rated)
        trending_recipes = Recipe.query.join(Recipe.ratings).group_by(Recipe.id).order_by(
            db.func.count(Recipe.ratings).desc()
        ).limit(6).all()
        
        # Convert to dict format
        trending_data = []
        for recipe in trending_recipes:
            recipe_dict = recipe.to_dict()
            recipe_dict['ingredients'] = json.loads(recipe.ingredients)[:3]  # Show first 3 ingredients
            trending_data.append(recipe_dict)
        
        return render_template('index.html', trending_recipes=trending_data)
        
    except Exception as e:
        logger.error(f"Index page error: {str(e)}")
        return render_template('index.html', trending_recipes=[])

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/meal-planner')
def meal_planner():
    return render_template('meal-planner.html')

@main_bp.route('/meal-plan', methods=['GET', 'POST'])
def meal_plan():
    try:
        # Check authentication
        user_id = None
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        
        if request.method == 'GET':
            # Get current week's meal plan
            week_start = request.args.get('week_start')
            if week_start:
                week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
            else:
                # Get current week start (Monday)
                today = datetime.now().date()
                week_start = today - timedelta(days=today.weekday())
            
            meal_plan = MealPlan.query.filter_by(
                user_id=user_id,
                week_start=week_start
            ).first()
            
            if meal_plan:
                plan_data = json.loads(meal_plan.plan_data)
                return jsonify({
                    'success': True,
                    'meal_plan': {
                        'week_start': week_start.isoformat(),
                        'plan': plan_data
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'meal_plan': {
                        'week_start': week_start.isoformat(),
                        'plan': {}
                    }
                })
        
        elif request.method == 'POST':
            # Save/update meal plan
            data = request.get_json()
            week_start = datetime.strptime(data['week_start'], '%Y-%m-%d').date()
            plan_data = data['plan']
            
            # Check if meal plan exists
            meal_plan = MealPlan.query.filter_by(
                user_id=user_id,
                week_start=week_start
            ).first()
            
            if meal_plan:
                meal_plan.plan_data = json.dumps(plan_data)
            else:
                meal_plan = MealPlan(
                    user_id=user_id,
                    week_start=week_start,
                    plan_data=json.dumps(plan_data)
                )
                db.session.add(meal_plan)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Meal plan saved successfully'
            })
            
    except Exception as e:
        logger.error(f"Meal plan error: {str(e)}")
        return jsonify({'success': False, 'message': 'Meal plan operation failed'}), 500

@main_bp.route('/api/search-recipes')
def search_recipes():
    try:
        query = request.args.get('q', '').strip()
        cuisine = request.args.get('cuisine', '')
        difficulty = request.args.get('difficulty', '')
        max_time = request.args.get('max_time', type=int)
        source_type = request.args.get('source_type', '')
        
        # Build query
        recipes_query = Recipe.query
        
        if query:
            recipes_query = recipes_query.filter(
                Recipe.title.contains(query) | 
                Recipe.ingredients.contains(query)
            )
        
        if cuisine:
            recipes_query = recipes_query.filter(Recipe.cuisine == cuisine)
        
        if difficulty:
            recipes_query = recipes_query.filter(Recipe.difficulty == difficulty)
        
        if max_time:
            recipes_query = recipes_query.filter(Recipe.cooking_time <= max_time)
            
        # Filter by source type (ai_generated, manual, imported)
        if source_type:
            recipes_query = recipes_query.filter(Recipe.source_type == source_type)
        
        recipes = recipes_query.limit(20).all()
        
        # Convert to dict format
        recipes_data = []
        for recipe in recipes:
            recipe_dict = recipe.to_dict()
            recipe_dict['ingredients'] = json.loads(recipe.ingredients)
            recipe_dict['instructions'] = json.loads(recipe.instructions)
            if recipe.flavor_profile:
                recipe_dict['flavor_profile'] = json.loads(recipe.flavor_profile)
            recipes_data.append(recipe_dict)
        
        return jsonify({
            'success': True,
            'recipes': recipes_data,
            'total': len(recipes_data)
        })
        
    except Exception as e:
        logger.error(f"Recipe search error: {str(e)}")
        return jsonify({'success': False, 'message': 'Search failed'}), 500

@main_bp.route('/api/cuisines')
def get_cuisines():
    try:
        cuisines = db.session.query(Recipe.cuisine).distinct().filter(
            Recipe.cuisine.isnot(None)
        ).all()
        
        cuisine_list = [cuisine[0] for cuisine in cuisines if cuisine]
        
        return jsonify({
            'success': True,
            'cuisines': sorted(cuisine_list)
        })
        
    except Exception as e:
        logger.error(f"Get cuisines error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch cuisines'})

@main_bp.route('/api/saved-recipes')
def get_saved_recipes():
    try:
        # Check authentication
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
            
        # Get user's saved recipes
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
        saved_recipes = user.saved_recipes
        
        # Convert to dict format
        recipes_data = []
        for recipe in saved_recipes:
            recipe_dict = recipe.to_dict()
            recipe_dict['ingredients'] = json.loads(recipe.ingredients)
            recipe_dict['instructions'] = json.loads(recipe.instructions)
            if recipe.flavor_profile:
                recipe_dict['flavor_profile'] = json.loads(recipe.flavor_profile)
            recipes_data.append(recipe_dict)
        
        return jsonify({
            'success': True,
            'recipes': recipes_data,
            'total': len(recipes_data)
        })
        
    except Exception as e:
        logger.error(f"Get saved recipes error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch saved recipes'}), 500
