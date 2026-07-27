"""
This module defines the authentication-related views for the web application using Flask's Blueprint feature. 
It includes routes for the dashboard, links management, and API endpoints for deleting and updating service links.
The views handle user authentication, session management, and interaction with the database to manage user-specific service links.
warning: This module assumes that the user is authenticated and has a valid session for accessing the dashboard and managing links.
what it does:
- Provides a dashboard view that displays the number of links, online links, and offline links for the authenticated user.
- Provides a links management view that allows users to view, add, update, and delete their service links.
- Implements API endpoints for deleting and updating service links, ensuring that only authenticated users can perform these actions.
- Redirects unauthenticated users to the login page when they attempt to access protected routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import requests

from database.model import User, service_linkes
from database.manage_db import Session, SESSION


auth_view = Blueprint(
    'auth_view',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)

@auth_view.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Renders the dashboard page for authenticated users.
    What it does:
    - Checks if the user is logged in by verifying the session.
    - If the user is logged in, it retrieves the number of links, online links, and offline links associated with the user from the database.
    - Renders the 'dashboard.html' template with the retrieved data.
    - If the user is not logged in or the session is invalid, it redirects to the login page.
    Returns:
    - The rendered 'dashboard.html' template with the user's link statistics if the user is authenticated.
    - A redirect to the login page if the user is not authenticated or the session is invalid
    """
    session_manger = Session()
    if 'user' in session:
        if SESSION(session.get('user'), 'check', session.get('session_id')):
            number_of_links = session_manger.query(service_linkes).filter_by(
                user_id=session.get('user')
            ).count()
            online_links = session_manger.query(service_linkes).filter_by(
                user_id=session.get('user'), status='online'
            ).count()
            offline_links = session_manger.query(service_linkes).filter_by(
                user_id=session.get('user'), status='offline'
            ).count()
            return render_template(
                'dashboard.html', 
                number_of_links=number_of_links, 
                online_links=online_links, 
                offline_links=offline_links
            )
        else:
            return redirect(url_for('login_view.login'))
    else:
        return redirect(url_for('login_view.login'))


@auth_view.route('/links_management', methods=['GET', 'POST'])
def links_management():
    """
    Handles the management of service links for authenticated users.
    What it does:
    - Checks if the user is logged in by verifying the session.
    - If the user is logged in, it allows them to view, add, update, or delete service links associated with their account.
    - For GET requests, it retrieves and displays the user's existing service links.
    - For POST requests, it allows the user to add a new service link to their account.
    - If the user is not logged in or the session is invalid, it redirects to the login page.
    Returns:
    - The rendered 'links_management.html' template with the user's service links for GET requests.
    - A redirect to the 'links_management' page after successfully adding a new service link for POST requests.
    - A redirect to the login page if the user is not authenticated or the session is invalid.
    - An error message in the 'links_management.html' template if the user attempts to add a new service link without providing a valid link.
    """
    if 'user' in session:
        session_manger = Session()
        if SESSION(session.get('user'), 'check', session.get('session_id')):
            if request.method == 'GET':
                user = session_manger.query(User).filter_by(username=session.get('user')).first()
                if user:
                    links = session_manger.query(service_linkes).filter_by(user_id=user.id).all()
                    return render_template('links_management.html', links=links)
                else:
                    return redirect(url_for('login_view.login'))
            # adding new link
            elif request.method == 'POST':
                service_link = request.form.get('service_link')
                if service_link:
                    user = session_manger.query(User).filter_by(
                        username=session.get('user')
                    ).first()
                    if user:
                        new_link = service_linkes(
                            ID=None,
                            user_id=user.id,
                            service_link=service_link
                        )
                        session_manger.add(new_link)
                        session_manger.commit()
                        return redirect(url_for('auth_view.links_management'))
                    else:
                        return redirect(url_for('auth_view.login'))
                else:
                    return render_template(
                        'links_management.html',
                        error='Please provide a valid service link.'
                    )
        else:
            return redirect(url_for('auth_view.login'))
    return render_template('links_management.html')


@auth_view.route('/api/links_management/delete/<int:link_id>', methods=['POST'])
def delete_link(link_id):
    """
    Handles the deletion of a service link for authenticated users.
    What it does:
    - Checks if the user is logged in by verifying the session.
    - If the user is logged in, it attempts to delete the specified service link associated with their account.
    - If the link is found and the user has permission to delete it, the link is removed from the database, and the user is redirected to the 'links_management' page.
    - If the link is not found or the user does not have permission to delete it, an error message is displayed on the 'links_management.html' template.
    - If the user is not logged in or the session is invalid, it redirects to the login page.
    Returns:
    - A redirect to the 'links_management' page after successfully deleting the service link.
    - A redirect to the login page if the user is not authenticated or the session is invalid.
    - An error message in the 'links_management.html' template if the link is not found or the user does not have permission to delete it.
    """
    session_manger = Session()
    if 'user' not in session:
        if SESSION(session.get('user'), 'check', session.get('session_id')):
            user = session_manger.query(User).filter_by(username=session.get('user')).first()
            if user:
                link_to_delete = session_manger.query(service_linkes).filter_by(
                    ID=link_id, user_id=user.id
                ).first()
                if link_to_delete:
                    session_manger.delete(link_to_delete)
                    session_manger.commit()
                    return redirect(url_for('auth_view.links_management'))
                else:
                    return render_template(
                        'links_management.html',
                        error='Link not found or you do not have permission to delete it.'
                    )
            else:
                return redirect(url_for('auth_view.login'))
        else:
            return redirect(url_for('auth_view.login'))
    return render_template('links_management.html')


@auth_view.route('/api/links_management/update/<int:link_id>', methods=['POST'])
def update_link(link_id):
    """
    Handles the updating of a service link for authenticated users.
    What it does:
    - Checks if the user is logged in by verifying the session.
    - If the user is logged in, it attempts to update the specified service link associated with their account.
    - If the link is found and the user has permission to update it, the link is updated in the database with the new service link provided in the request form, and the user is redirected to the 'links_management' page.
    - If the link is not found or the user does not have permission to update it, an error message is displayed on the 'links_management.html' template.
    - If the user is not logged in or the session is invalid, it redirects to the login page.
    Returns:
    - A redirect to the 'links_management' page after successfully updating the service link.
    - A redirect to the login page if the user is not authenticated or the session is invalid.
    - An error message in the 'links_management.html' template if the link is not found or the user does not have permission to update it, or if the new service link is not provided.
    """
    session_manger = Session()
    if 'user' in session:
        if SESSION(session.get('user'), 'check', session.get('session_id')):
            user = session_manger.query(User).filter_by(username=session.get('user')).first()
            if user:
                link_to_update = session_manger.query(service_linkes).filter_by(
                    ID=link_id, user_id=user.id
                ).first()
                if link_to_update:
                    new_service_link = request.form.get('service_link')
                    if new_service_link:
                        link_to_update.service_link = new_service_link
                        session_manger.commit()
                        return redirect(url_for('auth_view.links_management'))
                    else:
                        return render_template(
                            'links_management.html',
                            error='Please provide a valid service link.'
                        )
                else:
                    return render_template(
                        'links_management.html',
                        error='Link not found or you do not have permission to update it.'
                    )
            else:
                return redirect(url_for('auth_view.login'))
        else:
            return redirect(url_for('auth_view.login'))
    return render_template('links_management.html')


@auth_view.route('/is_the_like_alive')
def is_the_like_alive():
    session_manager = Session()
    
    try:
        # Check if user is logged in
        if 'user' not in session:
            return jsonify({'message': 'Please login first'}), 401
        
        # Check if session is valid
        if not SESSION(session.get('user'), 'check', session.get('session_id')):
            return jsonify({'message': 'Invalid session. Please login again.'}), 401
        
        # Get the user
        user = session_manager.query(User).filter_by(username=session.get('user')).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get all links for this user
        links = session_manager.query(service_linkes).filter_by(user_id=user.id).all()
        
        if not links:
            return jsonify({'message': {'online': [], 'offline': []}}), 200
        
        report = {
            'online': [],
            'offline': []
        }
        
        for link in links:
            try:
                # Send a HEAD request with timeout to check if link is alive
                r = requests.head(link.service_link, timeout=5, allow_redirects=True)
                if r.status_code == 200:
                    report['online'].append(link.service_link)
                else:
                    report['offline'].append(link.service_link)
            except Exception as e:
                report['offline'].append(link.service_link)
        
        return jsonify({'message': report}), 200
        
    except Exception as e:
        print(f"Error in is_the_like_alive: {e}")
        return jsonify({'message': 'An error occurred while checking links'}), 500
    finally:
        session_manager.close()


