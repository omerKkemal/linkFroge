import traceback

from flask import Blueprint, request, jsonify
from database.manage_db import get_session, SESSION, Session, config
from database.model import User, service_linkes
from datetime import datetime

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
        valid_link = session_manager.query(service_linkes).filter_by(ID=service_link_id).first()
        if not valid_link:
            return jsonify({'error': 'Service link not found'}), 404

        token = auth_token.split(" ")[1]
        valid_token = session_manager.query(User).filter_by(token=token).first()
        if not valid_token:
            return jsonify({'error': 'Invalid token'}), 401

        service_link = session_manager.query(service_linkes).filter_by(
            ID=service_link_id
        ).first()
        if not service_link:
            return jsonify({'error': 'Service link not found'}), 404

        return jsonify({'link': service_link.service_link}), 200
    except Exception as e:
        session_manager.rollback()
        print(f"Error in get_link: {traceback.format_exc()}")
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
        link = request.json.get('link')
        if not link:
            return jsonify({'error': 'Link is missing in the request body'}), 400
        user = session_manager.query(User).filter_by(token=token).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        new_service_link = service_linkes(
            ID=config.ID(10),
            service_link=link if link.startswith("http://") or link.startswith("https://") else f"http://{link}",
            user_id=user.id,
            visibility='private',
            catagory='frontend',
            create_at=datetime.now(),
            update_at=datetime.now()
        )
        session_manager.add(new_service_link)
        session_manager.commit()

        return jsonify({'service_link_id': new_service_link.ID}), 200
    except Exception as e:
        session_manager.rollback()
        print(f"Error in register_service: {traceback.format_exc()}")
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
        valid_link = session_manager.query(service_linkes).filter_by(ID=service_link_id).first()
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
            ID=service_link_id
        ).first()
        if not service_link:
            return jsonify({'error': 'Service link not found'}), 404

        if service_link.user_id != valid_token.ID:
            return jsonify({'error': 'Unauthorized to update this link'}), 403

        service_link.service_link = new_link
        service_link.updated_at = datetime.now()
        session_manager.commit()

        return jsonify({'message': 'Link updated successfully'}), 200
    except Exception as e:
        session_manager.rollback()
        print(f"Error in update_link: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

    finally:
        session_manager.close()

