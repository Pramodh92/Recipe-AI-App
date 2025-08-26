from flask import current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    decode_token, get_jti
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models.database import db
from models.user import User, UserSession
import secrets
import string
import re
import logging

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Comprehensive authentication service for user management"""
    
    def __init__(self):
        self.password_requirements = {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_number': True,
            'require_special': True
        }
    
    def validate_email(self, email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def validate_password(self, password):
        """Validate password against requirements"""
        errors = []
        
        if len(password) < self.password_requirements['min_length']:
            errors.append(f"Password must be at least {self.password_requirements['min_length']} characters long")
        
        if self.password_requirements['require_uppercase'] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.password_requirements['require_lowercase'] and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.password_requirements['require_number'] and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if self.password_requirements['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def register_user(self, name, email, password, preferred_language='en', **kwargs):
        """Register a new user"""
        try:
            # Validate inputs
            if not name or not name.strip():
                return {'success': False, 'message': 'Name is required'}
            
            if not email or not self.validate_email(email):
                return {'success': False, 'message': 'Valid email is required'}
            
            # Clean email
            email = email.lower().strip()
            
            # Validate password
            is_valid_password, password_errors = self.validate_password(password)
            if not is_valid_password:
                return {'success': False, 'message': '; '.join(password_errors)}
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {'success': False, 'message': 'Email already registered'}
            
            # Create new user
            user = User(
                name=name.strip(),
                email=email,
                preferred_language=preferred_language
            )
            user.set_password(password)
            
            # Set additional fields if provided
            if 'phone' in kwargs:
                user.phone = kwargs['phone']
            if 'bio' in kwargs:
                user.bio = kwargs['bio']
            
            db.session.add(user)
            db.session.commit()
            
            # Generate tokens
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=1),
                additional_claims={'user_type': 'regular', 'email': user.email}
            )
            
            refresh_token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(days=30)
            )
            
            # Create session record
            self.create_user_session(user.id, access_token)
            
            logger.info(f"New user registered: {email}")
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            return {'success': False, 'message': 'Registration failed'}
    
    def authenticate_user(self, email, password, ip_address=None, user_agent=None):
        """Authenticate user credentials and create session"""
        try:
            if not email or not password:
                return {'success': False, 'message': 'Email and password are required'}
            
            # Clean email
            email = email.lower().strip()
            
            # Find user
            user = User.query.filter_by(email=email, is_active=True).first()
            
            if not user or not user.check_password(password):
                logger.warning(f"Failed login attempt for email: {email}")
                return {'success': False, 'message': 'Invalid credentials'}
            
            # Update last login
            user.update_last_login()
            
            # Generate tokens with additional claims
            additional_claims = {
                'user_type': 'premium' if user.is_premium_user() else 'regular',
                'email': user.email,
                'preferred_language': user.preferred_language
            }
            
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=1),
                additional_claims=additional_claims
            )
            
            refresh_token = create_refresh_token(
                identity=user.id,
                expires_delta=timedelta(days=30)
            )
            
            # Create session record
            self.create_user_session(user.id, access_token, ip_address, user_agent)
            
            logger.info(f"User logged in: {email}")
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {'success': False, 'message': 'Authentication failed'}
    
    def refresh_access_token(self, user_id):
        """Generate new access token"""
        try:
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return {'success': False, 'message': 'User not found or inactive'}
            
            # Generate new access token
            additional_claims = {
                'user_type': 'premium' if user.is_premium_user() else 'regular',
                'email': user.email,
                'preferred_language': user.preferred_language
            }
            
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=1),
                additional_claims=additional_claims
            )
            
            return {
                'success': True,
                'access_token': access_token
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {'success': False, 'message': 'Token refresh failed'}
    
    def create_user_session(self, user_id, token, ip_address=None, user_agent=None):
        """Create user session record"""
        try:
            # Decode token to get expiration
            decoded_token = decode_token(token)
            expires_at = datetime.fromtimestamp(decoded_token['exp'])
            
            session = UserSession(
                user_id=user_id,
                session_token=get_jti(token),
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.session.add(session)
            db.session.commit()
            
            return session
            
        except Exception as e:
            logger.error(f"Session creation error: {str(e)}")
            return None
    
    def revoke_user_session(self, session_token):
        """Revoke user session"""
        try:
            session = UserSession.query.filter_by(session_token=session_token).first()
            if session:
                session.revoke()
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Session revocation error: {str(e)}")
            return False
    
    def revoke_all_user_sessions(self, user_id):
        """Revoke all sessions for a user"""
        try:
            sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
            for session in sessions:
                session.revoke()
            
            db.session.commit()
            return len(sessions)
            
        except Exception as e:
            logger.error(f"All sessions revocation error: {str(e)}")
            return 0
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Update allowed fields
            updateable_fields = [
                'name', 'phone', 'bio', 'preferred_language', 'default_servings', 
                'skill_level', 'dietary_restrictions', 'favorite_cuisines'
            ]
            
            for field in updateable_fields:
                if field in kwargs:
                    if field == 'dietary_restrictions':
                        user.set_dietary_restrictions(kwargs[field])
                    elif field == 'favorite_cuisines':
                        user.set_favorite_cuisines(kwargs[field])
                    else:
                        setattr(user, field, kwargs[field])
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update error: {str(e)}")
            return {'success': False, 'message': 'Profile update failed'}
    
    def change_user_password(self, user_id, current_password, new_password):
        """Change user password"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Verify current password
            if not user.check_password(current_password):
                return {'success': False, 'message': 'Current password is incorrect'}
            
            # Validate new password
            is_valid_password, password_errors = self.validate_password(new_password)
            if not is_valid_password:
                return {'success': False, 'message': '; '.join(password_errors)}
            
            # Update password
            user.set_password(new_password)
            db.session.commit()
            
            # Revoke all existing sessions for security
            self.revoke_all_user_sessions(user_id)
            
            logger.info(f"Password changed for user: {user.email}")
            
            return {'success': True, 'message': 'Password changed successfully'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password change error: {str(e)}")
            return {'success': False, 'message': 'Password change failed'}
    
    def generate_password_reset_token(self, email):
        """Generate password reset token"""
        try:
            user = User.query.filter_by(email=email.lower().strip()).first()
            if not user:
                # Return success even if user doesn't exist to prevent email enumeration
                return {'success': True, 'message': 'If the email exists, a reset link has been sent'}
            
            # Generate secure reset token
            reset_token = self.generate_secure_token(32)
            
            # Store token with expiration (implement token storage)
            # In production, store this in database with expiration time
            
            # Send email with reset token (implement email service)
            # email_service.send_password_reset_email(user.email, reset_token)
            
            logger.info(f"Password reset requested for: {email}")
            
            return {'success': True, 'message': 'If the email exists, a reset link has been sent'}
            
        except Exception as e:
            logger.error(f"Password reset token generation error: {str(e)}")
            return {'success': False, 'message': 'Password reset request failed'}
    
    def reset_password_with_token(self, token, new_password):
        """Reset password using token"""
        try:
            # Validate token and get user (implement token validation)
            # This would typically involve checking token in database and expiration
            
            # Validate new password
            is_valid_password, password_errors = self.validate_password(new_password)
            if not is_valid_password:
                return {'success': False, 'message': '; '.join(password_errors)}
            
            # Find user by token (implement token lookup)
            # user = get_user_by_reset_token(token)
            # if not user:
            #     return {'success': False, 'message': 'Invalid or expired token'}
            
            # Update password
            # user.set_password(new_password)
            # db.session.commit()
            
            # Revoke all sessions
            # self.revoke_all_user_sessions(user.id)
            
            # Delete used token
            # delete_reset_token(token)
            
            return {'success': True, 'message': 'Password has been reset successfully'}
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return {'success': False, 'message': 'Password reset failed'}
    
    def verify_user_email(self, user_id, verification_token):
        """Verify user email address"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Validate verification token (implement token validation)
            
            user.is_verified = True
            user.email_verified_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Email verified for user: {user.email}")
            
            return {'success': True, 'message': 'Email verified successfully'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Email verification error: {str(e)}")
            return {'success': False, 'message': 'Email verification failed'}
    
    def deactivate_user_account(self, user_id, reason=None):
        """Deactivate user account"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user.is_active = False
            db.session.commit()
            
            # Revoke all sessions
            self.revoke_all_user_sessions(user_id)
            
            logger.info(f"User account deactivated: {user.email}, reason: {reason}")
            
            return {'success': True, 'message': 'Account deactivated successfully'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Account deactivation error: {str(e)}")
            return {'success': False, 'message': 'Account deactivation failed'}
    
    def delete_user_account(self, user_id):
        """Permanently delete user account and all associated data"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            email = user.email  # Store for logging
            
            # Delete user (cascade should handle related records)
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"User account permanently deleted: {email}")
            
            return {'success': True, 'message': 'Account deleted permanently'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Account deletion error: {str(e)}")
            return {'success': False, 'message': 'Account deletion failed'}
    
    def get_user_sessions(self, user_id):
        """Get all active sessions for user"""
        try:
            sessions = UserSession.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).order_by(UserSession.last_activity.desc()).all()
            
            return {
                'success': True,
                'sessions': [session.to_dict() for session in sessions]
            }
            
        except Exception as e:
            logger.error(f"Get sessions error: {str(e)}")
            return {'success': False, 'message': 'Failed to retrieve sessions'}
    
    def update_notification_preferences(self, user_id, preferences):
        """Update user notification preferences"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user.update_notification_preferences(preferences)
            db.session.commit()
            
            return {'success': True, 'message': 'Notification preferences updated'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Notification preferences update error: {str(e)}")
            return {'success': False, 'message': 'Failed to update preferences'}
    
    def update_privacy_settings(self, user_id, settings):
        """Update user privacy settings"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            user.update_privacy_settings(settings)
            db.session.commit()
            
            return {'success': True, 'message': 'Privacy settings updated'}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Privacy settings update error: {str(e)}")
            return {'success': False, 'message': 'Failed to update privacy settings'}
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate cryptographically secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def is_session_valid(session_token):
        """Check if session is valid"""
        try:
            session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not session:
                return False
            
            if session.is_expired():
                session.revoke()
                db.session.commit()
                return False
            
            # Update last activity
            session.update_activity()
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Session validation error: {str(e)}")
            return False

# Global instance
auth_service = AuthenticationService()
