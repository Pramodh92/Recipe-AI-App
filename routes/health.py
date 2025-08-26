from flask import Blueprint, jsonify
import time
import logging

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)

# Store application start time
start_time = time.time()

@health_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    try:
        uptime = time.time() - start_time
        return jsonify({
            'status': 'ok',
            'uptime': uptime,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500