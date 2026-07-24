from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from webApp.database.manage_db import get_session, SESSION
from webApp.database.model import User, service_linkes
from datetime import datetime
import secrets

api = Blueprint('api', __name__)

# ================= HELPER FUNCTIONS =================

def get_user_by_token(token):
    """Get user by token"""
    db_session = get_session()
    try:
        user = db_session.query(User).filter_by(token=token).first()
        return user
    finally:
        db_session.close()

def get_user_by_id(user_id):
    """Get user by ID"""
    db_session = get_session()
    try:
        user = db_session.query(User).filter_by(id=user_id).first()
        return user
    finally:
        db_session.close()

def generate_service_token():
    """Generate a unique service token"""
    return secrets.token_urlsafe(32)

def validate_service_link(service_link):
    """Validate service link format"""
    if not service_link:
        return False
    if not service_link.startswith(('http://', 'https://')):
        return False
    return True

# ================= API ENDPOINTS =================

@api.route('/service/update', methods=['POST'])
def update_service():
    """
    Update service endpoint status
    
    Expected JSON payload:
    {
        "service_id": "abc123",  # This is the service token
        "url": "https://abc123.ngrok.io",
        "status": "online"  # or "offline"
    }
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]
        user = get_user_by_token(token)  # Validate user token (not used further here, but ensures the user is valid)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_id', 'url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        service_token = data['service_id']
        service_url = data['url']
        status = data.get('status', 'online')
        
        # Validate URL format
        if not validate_service_link(service_url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        db_session = get_session()
        
        try:
            # Find the service by token (stored in service_link field)
            service = db_session.query(service_linkes).filter_by(service_link=service_token).first()
            
            if not service:
                return jsonify({'error': 'Service not found'}), 404
            
            # Update the service URL
            service.service_link = service_url
            service.update_at = datetime.now()
            
            db_session.commit()
            
            return jsonify({
                'message': 'Service updated successfully',
                'service_id': service.ID,
                'url': service_url,
                'status': status
            }), 200
            
        finally:
            db_session.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/services', methods=['GET'])
def get_services():
    """
    Get all services for authenticated user
    
    Headers:
        Authorization: Bearer <user_token>
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Get user by token
    user = get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    db_session = get_session()
    try:
        services = db_session.query(service_linkes).filter_by(user_id=user.id).all()
        
        services_data = [{
            'id': service.ID,
            'service_token': service.service_link,  # This is the token used for service updates
            'created_at': service.create_at.isoformat() if service.create_at else None,
            'updated_at': service.update_at.isoformat() if service.update_at else None
        } for service in services]
        
        return jsonify({
            'services': services_data,
            'count': len(services_data)
        }), 200
        
    finally:
        db_session.close()

@api.route('/services', methods=['POST'])
def create_service():
    """
    Create a new service for authenticated user
    
    Headers:
        Authorization: Bearer <user_token>
    
    Request body (optional):
    {
        "service_name": "My Service"  # Optional, for future use
    }
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Get user by token
    user = get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    db_session = get_session()
    try:
        # Generate unique service token
        service_token = generate_service_token()
        
        # Check if token already exists (very unlikely but just in case)
        existing = db_session.query(service_linkes).filter_by(service_link=service_token).first()
        while existing:
            service_token = generate_service_token()
            existing = db_session.query(service_linkes).filter_by(service_link=service_token).first()
        
        # Create new service
        new_service = service_linkes(
            ID=None,  # Auto-increment
            user_id=user.id,
            service_link=service_token,
            create_at=datetime.now(),
            update_at=datetime.now()
        )
        
        db_session.add(new_service)
        db_session.commit()
        
        return jsonify({
            'message': 'Service created successfully',
            'service_id': new_service.ID,
            'service_token': service_token,
            'created_at': new_service.create_at.isoformat()
        }), 201
        
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@api.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    """
    Delete a service
    
    Headers:
        Authorization: Bearer <user_token>
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Get user by token
    user = get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    db_session = get_session()
    try:
        service = db_session.query(service_linkes).filter_by(
            ID=service_id,
            user_id=user.id
        ).first()
        
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        db_session.delete(service)
        db_session.commit()
        
        return jsonify({'message': 'Service deleted successfully'}), 200
        
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@api.route('/services/<int:service_id>/status', methods=['GET'])
def get_service_status(service_id):
    """
    Get service status (checks if the service is online by pinging the URL)
    
    Headers:
        Authorization: Bearer <user_token>
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    
    # Get user by token
    user = get_user_by_token(token)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    db_session = get_session()
    try:
        service = db_session.query(service_linkes).filter_by(
            ID=service_id,
            user_id=user.id
        ).first()
        
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Get the current URL (this would be the ngrok URL)
        current_url = service.service_link
        
        # You would typically check if the service is online here
        # For now, we'll just return the URL and last update time
        return jsonify({
            'service_id': service.ID,
            'current_url': current_url,
            'last_updated': service.update_at.isoformat() if service.update_at else None,
            'status': 'online'  # This would be determined by checking the URL
        }), 200
        
    finally:
        db_session.close()

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200