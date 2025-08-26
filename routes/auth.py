from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auth_service import auth_service
from models.database import db
from models.user import User
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Extract form data
        name = f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
        if not name:
            name = data.get('name', '').strip()
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        preferred_language = data.get('preferredLanguage', 'en')
        
        # Additional optional fields
        phone = data.get('phone')
        bio = data.get('bio')
        
        # Register user using auth service
        result = auth_service.register_user(
            name=name,
            email=email,
            password=password,
            preferred_language=preferred_language,
            phone=phone,
            bio=bio
        )
        
        if request.is_json:
            return jsonify(result), 201 if result['success'] else 400
        else:
            if result['success']:
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(result['message'], 'error')
                return render_template('auth/signup.html')
                
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        error_response = {'success': False, 'message': 'Registration failed'}
        
        if request.is_json:
            return jsonify(error_response), 500
        else:
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Get client info for session tracking
        ip_address = request.environ.get('REMOTE_ADDR')
        user_agent = request.headers.get('User-Agent')
        
        # Authenticate user using auth service
        result = auth_service.authenticate_user(
            email=email,
            password=password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if request.is_json:
            return jsonify(result), 200 if result['success'] else 401
        else:
            if result['success']:
                flash('Login successful!', 'success')
                redirect_url = request.args.get('redirect', url_for('main.index'))
                return redirect(redirect_url)
            else:
                flash(result['message'], 'error')
                return render_template('auth/login.html')
                
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        error_response = {'success': False, 'message': 'Login failed'}
        
        if request.is_json:
            return jsonify(error_response), 500
        else:
            flash('Login failed. Please try again.', 'error')
            return render_template('auth/login.html')

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        user_id = get_jwt_identity()
        result = auth_service.refresh_access_token(user_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'success': False, 'message': 'Token refresh failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # Get session token from JWT
        jwt_claims = get_jwt()
        session_token = jwt_claims.get('jti')  # JWT ID
        
        # Revoke session
        auth_service.revoke_user_session(session_token)
        
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'success': False, 'message': 'Logout failed'}), 500

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        
        if request.method == 'GET':
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'success': True, 'user': user.to_dict(include_sensitive=True)})
            else:
                # For HTML requests, ensure we're passing the user object to the template
                return render_template('profile.html', user=user)
        
        # PUT request - update profile
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        result = auth_service.update_user_profile(user_id, **data)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({'success': False, 'message': 'Profile operation failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False, 
                'message': 'Current and new passwords are required'
            }), 400
        
        result = auth_service.change_user_password(user_id, current_password, new_password)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({'success': False, 'message': 'Password change failed'}), 500

@auth_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    try:
        user_id = get_jwt_identity()
        result = auth_service.get_user_sessions(user_id)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get sessions'}), 500

@auth_bp.route('/sessions/revoke-all', methods=['POST'])
@jwt_required()
def revoke_all_sessions():
    try:
        user_id = get_jwt_identity()
        revoked_count = auth_service.revoke_all_user_sessions(user_id)
        
        return jsonify({
            'success': True, 
            'message': f'Revoked {revoked_count} sessions',
            'revoked_count': revoked_count
        }), 200
        
    except Exception as e:
        logger.error(f"Revoke all sessions error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to revoke sessions'}), 500

@auth_bp.route('/password-reset', methods=['POST'])
def password_reset_request():
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        result = auth_service.generate_password_reset_token(email)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return jsonify({'success': False, 'message': 'Password reset request failed'}), 500

@auth_bp.route('/password-reset/confirm', methods=['POST'])
def password_reset_confirm():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({
                'success': False, 
                'message': 'Token and new password are required'
            }), 400
        
        result = auth_service.reset_password_with_token(token, new_password)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Password reset confirm error: {str(e)}")
        return jsonify({'success': False, 'message': 'Password reset failed'}), 500

@auth_bp.route('/verify-email', methods=['POST'])
@jwt_required()
def verify_email():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        verification_token = data.get('token')
        
        if not verification_token:
            return jsonify({'success': False, 'message': 'Verification token is required'}), 400
        
        result = auth_service.verify_user_email(user_id, verification_token)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        return jsonify({'success': False, 'message': 'Email verification failed'}), 500

@auth_bp.route('/deactivate-account', methods=['POST'])
@jwt_required()
def deactivate_account():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        reason = data.get('reason', 'User requested')
        
        result = auth_service.deactivate_user_account(user_id, reason)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Account deactivation error: {str(e)}")
        return jsonify({'success': False, 'message': 'Account deactivation failed'}), 500

@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    try:
        user_id = get_jwt_identity()
        
        result = auth_service.delete_user_account(user_id)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Account deletion error: {str(e)}")
        return jsonify({'success': False, 'message': 'Account deletion failed'}), 500

@auth_bp.route('/preferences/notifications', methods=['PUT'])
@jwt_required()
def update_notifications():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = auth_service.update_notification_preferences(user_id, data)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Notification preferences error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update notifications'}), 500

@auth_bp.route('/preferences/privacy', methods=['PUT'])
@jwt_required()
def update_privacy():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        result = auth_service.update_privacy_settings(user_id, data)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Privacy settings error: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update privacy settings'}), 500
