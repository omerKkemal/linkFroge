from flask import Blueprint, request, jsonify
from database.manage_db import get_session, SESSION, Session
from database.model import User, service_linkes
from datetime import datetime
import secrets

api = Blueprint('api', __name__)

# get service link id from the hader and return the link if it exists in the database
@api.route('/get_link', methods=['GET'])
def get_link():

    session_manager = Session()
    try:
        service_link_id = request.headers.get('Service-Link-Id')
        if not service_link_id:
            return jsonify({'error': 'Service-Link-Id header is missing'}), 400
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({'error': 'Authorization header is missing'}), 400
        valid_link = session_manager.query(service_linkes).filter_by(id=service_link_id).first()
        if not valid_link:
            return jsonify({'error': 'Service link not found'}), 404

        token = auth_token.split(" ")[1]
        valid_token = session_manager.query(User).filter_by(token=token).first()
        if not valid_token:
            return jsonify({'error': 'Invalid token'}), 401

        service_link = session_manager.query(service_linkes).filter_by(
            id=service_link_id
        ).first()
        if not service_link:
            return jsonify({'error': 'Service link not found'}), 404

        return jsonify({'link': service_link.link}), 200
    except Exception as e:
        session_manager.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        session_manager.close()


@api.route('/register_service', methods=['POST'])
def register_service():
    session_manager = Session()
    try:
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({'error': 'Authorization header is missing'}), 400

        token = auth_token.split(" ")[1]
        valid_token = session_manager.query(User).filter_by(token=token).first()
        if not valid_token:
            return jsonify({'error': 'Invalid token'}), 401

        new_service_link_id = secrets.token_hex(16)
        new_service_link = service_linkes(
            id=new_service_link_id,
            link="",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session_manager.add(new_service_link)
        session_manager.commit()

        return jsonify({'service_link_id': new_service_link_id}), 201
    except Exception as e:
        session_manager.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        session_manager.close()


@api.route('/update_link', methods=['POST'])
def update_link():
    session_manager = Session()
    try:
        service_link_id = request.headers.get('Service-Link-Id')
        if not service_link_id:
            return jsonify({'error': 'Service-Link-Id header is missing'}), 400
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({'error': 'Authorization header is missing'}), 400
        valid_link = session_manager.query(service_linkes).filter_by(id=service_link_id).first()
        if not valid_link:
            return jsonify({'error': 'Service link not found'}), 404

        token = auth_token.split(" ")[1]
        valid_token = session_manager.query(User).filter_by(token=token).first()
        if not valid_token:
            return jsonify({'error': 'Invalid token'}), 401

        new_link = request.json.get('link')
        if not new_link:
            return jsonify({'error': 'New link is missing in the request body'}), 400

        service_link = session_manager.query(service_linkes).filter_by(
            id=service_link_id
        ).first()
        if not service_link:
            return jsonify({'error': 'Service link not found'}), 404

        service_link.link = new_link
        service_link.updated_at = datetime.now()
        session_manager.commit()

        return jsonify({'message': 'Link updated successfully'}), 200
    except Exception as e:
        session_manager.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        session_manager.close()

