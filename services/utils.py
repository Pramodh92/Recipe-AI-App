from flask import current_app
import os
import json
import logging
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import base64

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Generate PDFs for shopping lists and meal plans"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#007bff')
        )
        
    def generate_shopping_list_pdf(self, shopping_list, filename=None):
        """Generate PDF for shopping list"""
        try:
            if not filename:
                filename = f"shopping_list_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            story = []
            
            # Title
            title = Paragraph("Shopping List", self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Date and stats
            date_info = Paragraph(
                f"Generated on: {datetime.now().strftime('%B %d, %Y')}<br/>"
                f"Total Items: {shopping_list.get('total_items', 0)}<br/>"
                f"Estimated Cost: {shopping_list.get('estimated_cost', '$0')}",
                self.styles['Normal']
            )
            story.append(date_info)
            story.append(Spacer(1, 20))
            
            # Categories and items
            for category, items in shopping_list.get('categories', {}).items():
                # Category header
                cat_header = Paragraph(f"{category} ({len(items)} items)", 
                                     self.styles['Heading2'])
                story.append(cat_header)
                story.append(Spacer(1, 6))
                
                # Items table
                data = [['☐', 'Item']]
                for item in items:
                    data.append(['☐', item])
                
                table = Table(data, colWidths=[0.5*inch, 5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
            
            doc.build(story)
            buffer.seek(0)
            
            return buffer.getvalue(), filename
            
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            raise
    
    def generate_meal_plan_pdf(self, meal_plan, week_start, filename=None):
        """Generate PDF for meal plan"""
        try:
            if not filename:
                filename = f"meal_plan_{week_start.strftime('%Y%m%d')}.pdf"
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            story = []
            
            # Title
            week_end = week_start + timedelta(days=6)
            title = Paragraph(
                f"Meal Plan<br/>{week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}",
                self.title_style
            )
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Meal plan table
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            meals = ['Breakfast', 'Lunch', 'Dinner']
            
            # Create table data
            data = [['Day'] + meals]
            
            for day in days:
                row = [day]
                day_key = day.lower()
                
                for meal in meals:
                    meal_key = meal.lower()
                    if (day_key in meal_plan and 
                        meal_key in meal_plan[day_key]):
                        meal_info = meal_plan[day_key][meal_key]
                        row.append(meal_info.get('title', 'N/A'))
                    else:
                        row.append('')
                
                data.append(row)
            
            table = Table(data, colWidths=[1.2*inch, 1.8*inch, 1.8*inch, 1.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 30))
            
            # Recipe details
            recipe_details = Paragraph("Recipe Details", self.styles['Heading2'])
            story.append(recipe_details)
            story.append(Spacer(1, 12))
            
            for day_key, day_meals in meal_plan.items():
                for meal_key, meal_info in day_meals.items():
                    if meal_info.get('title'):
                        recipe_title = Paragraph(
                            f"<b>{meal_info['title']}</b> ({day_key.title()} {meal_key.title()})",
                            self.styles['Heading3']
                        )
                        story.append(recipe_title)
                        
                        if meal_info.get('cooking_time'):
                            time_info = Paragraph(
                                f"Cooking Time: {meal_info['cooking_time']} minutes",
                                self.styles['Normal']
                            )
                            story.append(time_info)
                        
                        if meal_info.get('servings'):
                            servings_info = Paragraph(
                                f"Servings: {meal_info['servings']}",
                                self.styles['Normal']
                            )
                            story.append(servings_info)
                        
                        story.append(Spacer(1, 12))
            
            doc.build(story)
            buffer.seek(0)
            
            return buffer.getvalue(), filename
            
        except Exception as e:
            logger.error(f"Meal plan PDF generation error: {str(e)}")
            raise

class DataExporter:
    """Export user data in various formats"""
    
    @staticmethod
    def export_user_data(user_id):
        """Export all user data as JSON"""
        try:
            from models.database import db, Recipe, SavedRecipe, Rating, MealPlan, ShoppingList
            from models.user import User
            
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get user's saved recipes
            saved_recipes = db.session.query(Recipe).join(SavedRecipe).filter(
                SavedRecipe.user_id == user_id
            ).all()
            
            # Get user's ratings
            ratings = Rating.query.filter_by(user_id=user_id).all()
            
            # Get user's meal plans
            meal_plans = MealPlan.query.filter_by(user_id=user_id).all()
            
            # Get user's shopping lists
            shopping_lists = ShoppingList.query.filter_by(user_id=user_id).all()
            
            data = {
                'user_info': user.to_dict(),
                'saved_recipes': [recipe.to_dict() for recipe in saved_recipes],
                'ratings': [{
                    'recipe_id': rating.recipe_id,
                    'rating': rating.rating,
                    'comment': rating.comment,
                    'created_at': rating.created_at.isoformat()
                } for rating in ratings],
                'meal_plans': [{
                    'week_start': meal_plan.week_start.isoformat(),
                    'plan_data': meal_plan.plan_data,
                    'created_at': meal_plan.created_at.isoformat()
                } for meal_plan in meal_plans],
                'shopping_lists': [shopping_list.to_dict() for shopping_list in shopping_lists],
                'export_date': datetime.utcnow().isoformat()
            }
            
            return json.dumps(data, indent=2)
            
        except Exception as e:
            logger.error(f"Data export error: {str(e)}")
            raise

class ImageProcessor:
    """Process and optimize images"""
    
    @staticmethod
    def process_recipe_image(image_data, max_width=800, max_height=600):
        """Process and optimize recipe images"""
        try:
            from PIL import Image
            
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Resize if necessary
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise

class CacheManager:
    """Simple in-memory cache for frequent operations"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self.default_ttl = 300  # 5 minutes
    
    def get(self, key):
        """Get item from cache"""
        if key in self._cache:
            # Check if expired
            if (datetime.now() - self._timestamps[key]).seconds > self.default_ttl:
                self.delete(key)
                return None
            return self._cache[key]
        return None
    
    def set(self, key, value, ttl=None):
        """Set item in cache"""
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
    
    def delete(self, key):
        """Delete item from cache"""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._timestamps.clear()

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename for safe storage"""
        import re
        # Remove path components
        filename = os.path.basename(filename)
        # Remove or replace unsafe characters
        filename = re.sub(r'[^\w\s-.]', '', filename)
        # Replace spaces with underscores
        filename = re.sub(r'[\s]+', '_', filename)
        return filename
    
    @staticmethod
    def validate_file_type(filename, allowed_types):
        """Validate file type by extension"""
        if not filename:
            return False
        
        extension = filename.rsplit('.', 1)[-1].lower()
        return extension in allowed_types
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate secure random token"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

class EmailUtils:
    """Email utility functions (for future implementation)"""
    
    @staticmethod
    def send_welcome_email(user_email, user_name):
        """Send welcome email to new users"""
        # Placeholder for email functionality
        logger.info(f"Would send welcome email to {user_email}")
    
    @staticmethod
    def send_password_reset_email(user_email, reset_token):
        """Send password reset email"""
        # Placeholder for email functionality
        logger.info(f"Would send password reset email to {user_email}")

# Global instances
pdf_generator = PDFGenerator()
cache_manager = CacheManager()
