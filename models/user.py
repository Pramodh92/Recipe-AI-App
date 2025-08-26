from datetime import datetime
import bcrypt
import json
from flask_login import UserMixin
from models import db

class User(db.Model, UserMixin):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    preferred_language = db.Column(db.String(10), default='en')
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # User preferences
    dietary_restrictions = db.Column(db.Text, nullable=True)  # JSON string
    favorite_cuisines = db.Column(db.Text, nullable=True)  # JSON string
    default_servings = db.Column(db.Integer, default=4)
    skill_level = db.Column(db.String(20), default='intermediate')
    
    # Notification preferences
    recipe_notifications = db.Column(db.Boolean, default=True)
    meal_plan_notifications = db.Column(db.Boolean, default=True)
    shopping_notifications = db.Column(db.Boolean, default=False)
    tips_notifications = db.Column(db.Boolean, default=True)
    
    # Privacy settings
    allow_sharing = db.Column(db.Boolean, default=True)
    analytics_enabled = db.Column(db.Boolean, default=True)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    saved_recipes = db.relationship('SavedRecipe', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    meal_plans = db.relationship('MealPlan', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    shopping_lists = db.relationship('ShoppingList', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    user_sessions = db.relationship('UserSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, name, email, preferred_language='en'):
        self.name = name
        self.email = email.lower().strip()
        self.preferred_language = preferred_language
    
    def set_password(self, password):
        """Hash and set user password"""
        if not password:
            raise ValueError("Password cannot be empty")
        
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        if not password or not self.password_hash:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_at = datetime.utcnow()
        db.session.commit()
    
    def set_dietary_restrictions(self, restrictions_list):
        """Set dietary restrictions as JSON"""
        if restrictions_list:
            self.dietary_restrictions = json.dumps(restrictions_list)
        else:
            self.dietary_restrictions = None
    
    def get_dietary_restrictions(self):
        """Get dietary restrictions as list"""
        if self.dietary_restrictions:
            try:
                return json.loads(self.dietary_restrictions)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_favorite_cuisines(self, cuisines_list):
        """Set favorite cuisines as JSON"""
        if cuisines_list:
            self.favorite_cuisines = json.dumps(cuisines_list)
        else:
            self.favorite_cuisines = None
    
    def get_favorite_cuisines(self):
        """Get favorite cuisines as list"""
        if self.favorite_cuisines:
            try:
                return json.loads(self.favorite_cuisines)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_recipe_count(self):
        """Get count of saved recipes"""
        return self.saved_recipes.count()
    
    def get_meal_plan_count(self):
        """Get count of meal plans"""
        return self.meal_plans.count()
    
    def get_shopping_list_count(self):
        """Get count of shopping lists"""
        return self.shopping_lists.count()
    
    def get_average_recipe_rating(self):
        """Get user's average rating given to recipes"""
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0.0
    
    def has_rated_recipe(self, recipe_id):
        """Check if user has rated a specific recipe"""
        return self.ratings.filter_by(recipe_id=recipe_id).first() is not None
    
    def has_saved_recipe(self, recipe_id):
        """Check if user has saved a specific recipe"""
        return self.saved_recipes.filter_by(recipe_id=recipe_id).first() is not None
    
    def get_notification_preferences(self):
        """Get all notification preferences as dict"""
        return {
            'recipe_notifications': self.recipe_notifications,
            'meal_plan_notifications': self.meal_plan_notifications,
            'shopping_notifications': self.shopping_notifications,
            'tips_notifications': self.tips_notifications
        }
    
    def update_notification_preferences(self, preferences):
        """Update notification preferences"""
        if 'recipe_notifications' in preferences:
            self.recipe_notifications = preferences['recipe_notifications']
        if 'meal_plan_notifications' in preferences:
            self.meal_plan_notifications = preferences['meal_plan_notifications']
        if 'shopping_notifications' in preferences:
            self.shopping_notifications = preferences['shopping_notifications']
        if 'tips_notifications' in preferences:
            self.tips_notifications = preferences['tips_notifications']
    
    def get_privacy_settings(self):
        """Get privacy settings as dict"""
        return {
            'allow_sharing': self.allow_sharing,
            'analytics_enabled': self.analytics_enabled
        }
    
    def update_privacy_settings(self, settings):
        """Update privacy settings"""
        if 'allow_sharing' in settings:
            self.allow_sharing = settings['allow_sharing']
        if 'analytics_enabled' in settings:
            self.analytics_enabled = settings['analytics_enabled']
    
    def get_user_stats(self):
        """Get comprehensive user statistics"""
        return {
            'recipes_saved': self.get_recipe_count(),
            'meal_plans_created': self.get_meal_plan_count(),
            'shopping_lists_created': self.get_shopping_list_count(),
            'average_rating_given': round(self.get_average_recipe_rating(), 1),
            'account_age_days': (datetime.utcnow() - self.created_at).days,
            'last_active': self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    def is_premium_user(self):
        """Check if user has premium features (placeholder for future implementation)"""
        # Placeholder for premium user logic
        return False
    
    def can_generate_recipe(self):
        """Check if user can generate recipes (rate limiting placeholder)"""
        # Placeholder for rate limiting logic
        return True
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        user_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'preferred_language': self.preferred_language,
            'phone': self.phone,
            'bio': self.bio,
            'default_servings': self.default_servings,
            'skill_level': self.skill_level,
            'dietary_restrictions': self.get_dietary_restrictions(),
            'favorite_cuisines': self.get_favorite_cuisines(),
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'stats': self.get_user_stats()
        }
        
        if include_sensitive:
            user_dict.update({
                'notification_preferences': self.get_notification_preferences(),
                'privacy_settings': self.get_privacy_settings(),
                'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
                'is_active': self.is_active
            })
        
        return user_dict
    
    def to_public_dict(self):
        """Convert user to dictionary for public display (minimal info)"""
        return {
            'id': self.id,
            'name': self.name,
            'skill_level': self.skill_level,
            'favorite_cuisines': self.get_favorite_cuisines(),
            'member_since': self.created_at.strftime('%B %Y'),
            'recipe_count': self.get_recipe_count()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class UserSession(db.Model):
    """Track user sessions for security and analytics"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.String(512), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def revoke(self):
        """Revoke session"""
        self.is_active = False
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active
        }

class UserPreference(db.Model):
    """Store additional user preferences and settings"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preference_key = db.Column(db.String(100), nullable=False)
    preference_value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'preference_key', name='_user_preference_uc'),)
    
    @staticmethod
    def set_preference(user_id, key, value):
        """Set or update user preference"""
        preference = UserPreference.query.filter_by(user_id=user_id, preference_key=key).first()
        
        if preference:
            preference.preference_value = json.dumps(value) if not isinstance(value, str) else value
            preference.updated_at = datetime.utcnow()
        else:
            preference = UserPreference(
                user_id=user_id,
                preference_key=key,
                preference_value=json.dumps(value) if not isinstance(value, str) else value
            )
            db.session.add(preference)
    
    @staticmethod
    def get_preference(user_id, key, default=None):
        """Get user preference"""
        preference = UserPreference.query.filter_by(user_id=user_id, preference_key=key).first()
        
        if preference:
            try:
                return json.loads(preference.preference_value)
            except (json.JSONDecodeError, TypeError):
                return preference.preference_value
        
        return default
    
    @staticmethod
    def delete_preference(user_id, key):
        """Delete user preference"""
        preference = UserPreference.query.filter_by(user_id=user_id, preference_key=key).first()
        if preference:
            db.session.delete(preference)
    
    def to_dict(self):
        """Convert preference to dictionary"""
        try:
            value = json.loads(self.preference_value)
        except (json.JSONDecodeError, TypeError):
            value = self.preference_value
        
        return {
            'key': self.preference_key,
            'value': value,
            'updated_at': self.updated_at.isoformat()
        }
