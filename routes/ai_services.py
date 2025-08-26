from flask import Blueprint, request, jsonify, render_template, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from services.ai_client import ai_client
from models.database import ShoppingList, db
from models.user import User
from services.utils import pdf_generator
import json
import logging

ai_bp = Blueprint('ai_services', __name__)
logger = logging.getLogger(__name__)

@ai_bp.route('/encyclopedia')
def encyclopedia_page():
    return render_template('encyclopedia.html')

@ai_bp.route('/culinary-encyclopedia', methods=['POST'])
async def culinary_encyclopedia():
    try:
        # Optional authentication for language preference
        user_id = None
        language = 'en'
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                if user:
                    language = user.preferred_language
        except:
            pass
        
        data = request.get_json() if request.is_json else request.form
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'message': 'Query is required'}), 400
        
        result = await ai_client.explain_culinary_concept(query, language)
        
        if not result['success']:
            return jsonify({'success': False, 'message': 'Explanation generation failed'}), 500
        
        return jsonify({
            'success': True,
            'explanation': result['explanation']
        })
        
    except Exception as e:
        logger.error(f"Culinary encyclopedia error: {str(e)}")
        return jsonify({'success': False, 'message': 'Explanation failed'}), 500

@ai_bp.route('/substitute-ingredient', methods=['POST'])
async def substitute_ingredient():
    try:
        # Get user language preference
        user_id = None
        language = 'en'
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                if user:
                    language = user.preferred_language
        except:
            pass
        
        data = request.get_json() if request.is_json else request.form
        ingredient = data.get('ingredient', '').strip()
        context = data.get('context', '')
        
        if not ingredient:
            return jsonify({'success': False, 'message': 'Ingredient is required'}), 400
        
        result = await ai_client.suggest_ingredient_substitution(ingredient, context, language)
        
        if not result['success']:
            return jsonify({'success': False, 'message': 'Substitution suggestion failed'}), 500
        
        return jsonify({
            'success': True,
            'substitutions': result['data']
        })
        
    except Exception as e:
        logger.error(f"Ingredient substitution error: {str(e)}")
        return jsonify({'success': False, 'message': 'Substitution failed'}), 500

@ai_bp.route('/flavor-profile', methods=['POST'])
async def analyze_flavor_profile():
    try:
        # Get user language preference
        user_id = None
        language = 'en'
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                if user:
                    language = user.preferred_language
        except:
            pass
        
        data = request.get_json()
        recipe_text = data.get('recipe_text', '').strip()
        
        if not recipe_text:
            return jsonify({'success': False, 'message': 'Recipe text is required'}), 400
        
        result = await ai_client.analyze_flavor_profile(recipe_text, language)
        
        if not result['success']:
            return jsonify({'success': False, 'message': 'Flavor analysis failed'}), 500
        
        return jsonify({
            'success': True,
            'analysis': result['data']
        })
        
    except Exception as e:
        logger.error(f"Flavor analysis error: {str(e)}")
        return jsonify({'success': False, 'message': 'Flavor analysis failed'}), 500

@ai_bp.route('/shopping-list', methods=['GET', 'POST'])
async def shopping_list():
    if request.method == 'GET':
        return render_template('shopping-list.html')
    
    try:
        # Get user language preference
        user_id = None
        language = 'en'
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                if user:
                    language = user.preferred_language
        except:
            pass
        
        data = request.get_json()
        recipes = data.get('recipes', [])
        list_name = data.get('name', 'My Shopping List')
        
        if not recipes:
            return jsonify({'success': False, 'message': 'At least one recipe is required'}), 400
        
        result = await ai_client.generate_shopping_list(recipes, language)
        
        if not result['success']:
            return jsonify({'success': False, 'message': 'Shopping list generation failed'}), 500
        
        # Save shopping list if user is authenticated
        if user_id:
            # Extract recipe IDs from the recipes data
            recipe_ids = [recipe.get('id') for recipe in recipes if recipe.get('id')]
            
            shopping_list = ShoppingList(
                user_id=user_id,
                name=list_name,
                items=json.dumps(result['data']),
                source_recipes=json.dumps(recipe_ids) if recipe_ids else None
            )
            db.session.add(shopping_list)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'shopping_list': result['data']
        })
        
    except Exception as e:
        logger.error(f"Shopping list error: {str(e)}")
        return jsonify({'success': False, 'message': 'Shopping list generation failed'}), 500

@ai_bp.route('/translate-content', methods=['POST'])
async def translate_content():
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        target_language = data.get('target_language', 'en')
        
        if not content:
            return jsonify({'success': False, 'message': 'Content is required'}), 400
        
        result = await ai_client.translate_content(content, target_language)
        
        if not result['success']:
            return jsonify({'success': False, 'message': 'Translation failed'}), 500
        
        return jsonify({
            'success': True,
            'translated_text': result['translated_text']
        })
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({'success': False, 'message': 'Translation failed'}), 500

@ai_bp.route('/user-shopping-lists')
@jwt_required()
def get_user_shopping_lists():
    try:
        user_id = get_jwt_identity()
        
        shopping_lists = ShoppingList.query.filter_by(user_id=user_id).order_by(
            ShoppingList.created_at.desc()
        ).all()
        
        lists_data = []
        for shopping_list in shopping_lists:
            list_dict = shopping_list.to_dict()
            list_dict['items'] = json.loads(shopping_list.items)
            lists_data.append(list_dict)
        
        return jsonify({'success': True, 'shopping_lists': lists_data})
        
    except Exception as e:
        logger.error(f"Get shopping lists error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to fetch shopping lists'}), 500

@ai_bp.route('/shopping-list/export-pdf', methods=['POST'])
def export_shopping_list_pdf():
    try:
        data = request.get_json()
        shopping_list = data.get('shopping_list')
        list_name = data.get('name', 'Shopping List')
        
        if not shopping_list:
            return jsonify({'success': False, 'message': 'Shopping list data is required'}), 400
        
        # Generate PDF using the PDFGenerator utility
        pdf_data, filename = pdf_generator.generate_shopping_list_pdf(shopping_list, f"{list_name}.pdf")
        
        # Return PDF as attachment
        return send_file(
            pdf_data,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to generate PDF'}), 500

@ai_bp.route('/meal-plan/export-pdf', methods=['POST'])
def export_meal_plan_pdf():
    """Export meal plan as PDF"""
    try:
        from datetime import datetime
        
        # Get meal plan data from request
        data = request.get_json()
        meal_plan = data.get('meal_plan')
        week_start_str = data.get('week_start')
        
        if not meal_plan:
            return jsonify({'success': False, 'message': 'No meal plan data provided'}), 400
        
        # Parse week start date
        try:
            week_start = datetime.fromisoformat(week_start_str) if week_start_str else datetime.now()
        except ValueError:
            week_start = datetime.now()
        
        # Generate PDF
        pdf_data, filename = pdf_generator.generate_meal_plan_pdf(meal_plan, week_start)
        
        # Return PDF as attachment
        return send_file(
            pdf_data,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Meal plan PDF export error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to generate meal plan PDF'}), 500
