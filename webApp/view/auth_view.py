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

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
import requests
import traceback
from datetime import datetime

from database.model import User, service_linkes, comment, comment_reply
from database.manage_db import Session, SESSION, config


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
    session_manager = Session()
    try:
        if 'user' in session:
            
            if SESSION(session.get('user'), 'check', session.get('session_id')):
                user = session_manager.query(User).filter_by(username=session.get('user')).first()
                number_of_links = session_manager.query(service_linkes).filter_by(
                    user_id=user.id
                ).count()
                online_links = session_manager.query(service_linkes).filter_by(
                    user_id=user.id, status='online'
                ).count()
                offline_links = session_manager.query(service_linkes).filter_by(
                    user_id=user.id, status='offline'
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
    except Exception as e:
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the excepton(error): {e}')
        session_manager.rollback()
        flash("unKnown error :( try")
        return redirect('login_view.login')
    finally:
        session_manager.close()


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
    session_manager = Session()
    try:
        if 'user' in session:
            if SESSION(session.get('user'), 'check', session.get('session_id')):
                if request.method == 'GET':
                    user = session_manager.query(User).filter_by(username=session.get('user')).first()
                    if user:
                        links = session_manager.query(service_linkes).filter_by(user_id=user.id).all()
                        return render_template('links_management.html', links=links, catagorys=list(config.CATEGORY.items()))
                    else:
                        return redirect(url_for('login_view.login'))
                # adding new link
                elif request.method == 'POST':
                    service_link = request.form.get('service_link')
                    visibility = request.form.get('visibility')
                    catagory = request.form.get('catagory')
                    if service_link:
                        user = session_manager.query(User).filter_by(
                            username=session.get('user')
                        ).first()
                        r = requests.head(service_link, timeout=5, allow_redirects=True)
                        if r.status_code == 200:
                            status = 'online'
                        else:
                            status = 'offline'
                        if user:
                            new_link = service_linkes(
                                ID=config.ID(10),
                                user_id=user.id,
                                service_link=service_link,
                                visibility=visibility,
                                catagory=catagory,
                                status=status
                            )
                            session_manager.add(new_link)
                            session_manager.commit()
                            return redirect(url_for('auth_view.links_management'))
                        else:
                            return redirect(url_for('auth_view.login'))
                    else:
                        return render_template(
                            'links_management.html',
                            error='Please provide a valid service link.'
                        )
            else:
                return redirect(url_for('login_view.login'))
        return redirect(url_for('login_view.login'))
    except Exception as e:
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the excepton(error): {e}')
        session_manager.rollback()
        flash("unKnown error :( try")
        return redirect('login_view.login')
    finally:
        session_manager.close()


@auth_view.route('/api/links_management/delete/<string:link_id>', methods=['POST'])
def delete_link(link_id):
    """
    Handles the deletion of a service link for authenticated users.
    """
    session_manager = Session()
    try:
        
        # Check if user is logged in
        if 'user' not in session or 'session_id' not in session:
            return redirect(url_for('auth_view.login'))
        
        # Validate session
        if not SESSION(session.get('user'), 'check', session.get('session_id')):
            return redirect(url_for('auth_view.login'))
        
        # Get user
        user = session_manager.query(User).filter_by(username=session.get('user')).first()
        if not user:
            return redirect(url_for('auth_view.login'))
        
        # Find the link
        link_to_delete = session_manager.query(service_linkes).filter_by(
            ID=link_id, user_id=user.id
        ).first()
        
        if not link_to_delete:
            flash('Link not found or you do not have permission to delete it.', 'error')
            return redirect(url_for('auth_view.links_management'))
        
        # Delete the link
        session_manager.delete(link_to_delete)
        session_manager.commit()
        
        flash('Link deleted successfully.', 'success')
        return redirect(url_for('auth_view.links_management'))
    except Exception as e:
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the excepton(error): {e}')
        session_manager.rollback()
        flash("unKnown error :( try")
        return redirect('login_view.login')
    finally:
        session_manager.close()


@auth_view.route('/api/links_management/update/<link_id>', methods=['POST'])
def update_link(link_id):
    """
    Handles the updating of a service link for authenticated users.
    """
    session_manager = Session()
    try:
        
        # Check if user is logged in
        if 'user' not in session or 'session_id' not in session:
            return redirect(url_for('auth_view.login'))
        
        # Validate session
        if not SESSION(session.get('user'), 'check', session.get('session_id')):
            return redirect(url_for('auth_view.login'))
        
        # Get user
        user = session_manager.query(User).filter_by(username=session.get('user')).first()
        if not user:
            return redirect(url_for('auth_view.login'))
        
        # Find the link
        link_to_update = session_manager.query(service_linkes).filter_by(
            ID=link_id, user_id=user.id
        ).first()
        
        if not link_to_update:
            flash('Link not found or you do not have permission to update it.', 'error')
            return redirect(url_for('auth_view.links_management'))
        
        # Get new service link from form
        new_service_link = request.form.get('service_link')
        new_catagory = request.form.get('catagory')
        new_visibility = request.form.get('visibility')
        if not new_service_link:
            flash('Please provide a valid service link.', 'error')
            return redirect(url_for('auth_view.links_management'))
        
        # Update the link
        link_to_update.service_link = new_service_link
        link_to_update.catagory = new_catagory
        link_to_update.visibility = new_visibility
        link_to_update.update_at = datetime.now()
        session_manager.commit()
        
        flash('Link updated successfully.', 'success')
        return redirect(url_for('auth_view.links_management'))
    except Exception as e:
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the excepton(error): {e}')
        session_manager.rollback()
        flash("unKnown error :( try")
        return redirect('login_view.login')
    finally:
        session_manager.close()


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
        config.log(f'[Error] : {request.endpoint} the excepton(error): {e}')
        return jsonify({'message': 'An error occurred while checking links'}), 500
    finally:
        session_manager.close()


@auth_view.route('/api/comment', methods=['POST'])  # Added methods=['POST']
def comment_api():
    """
    Create a new comment on a link
    """
    session_manager = Session()
    try:
        # Check if user is logged in
        if 'user' not in session or 'session_id' not in session:
            return jsonify({"message": "Please login first"}), 401
        
        if not SESSION(session.get('user'), 'check', session.get('session_id')):
            return jsonify({'message': 'Invalid session. Please login again.'}), 401
        
        # Get form data
        comment_content = request.form.get('comment_content')
        link_id = request.form.get('link_id')  # Add link_id
        comment_by = session['user']
        
        # Validate input
        if not comment_content:
            return jsonify({"message": "Comment content is required"}), 400
        
        if not link_id:
            return jsonify({"message": "Link ID is required"}), 400
        
        # Create comment
        comment_obj = comment(
            ID=config.ID(),
            comment_content=comment_content,
            comment_by=comment_by,
            link_id=link_id,  # Add link_id to model
            create_at=datetime.now(),
            update_at=datetime.now()
        )
        session_manager.add(comment_obj)
        session_manager.commit()
        
        # Return the created comment data
        return jsonify({
            "message": "Comment was added successfully",
            "comment": {
                "id": comment_obj.ID,
                "content": comment_obj.comment_content,
                "by": comment_obj.comment_by,
                "created_at": comment_obj.create_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error in comment_api: {e}")
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the exception(error): {e}')
        return jsonify({'message': 'An error occurred while commenting'}), 500
    finally:
        session_manager.close()


@auth_view.route("/api/comment/update/<string:ID>", methods=['POST'])  # Added methods=['POST']
def update_comment(ID):
    """
    Update an existing comment
    """
    session_manager = Session()
    try:
        # Check if user is logged in
        if 'user' not in session or 'session_id' not in session:
            return jsonify({"message": "Please login first"}), 401
        
        if not SESSION(session.get('user'), 'check', session.get('session_id')):
            return jsonify({'message': 'Invalid session. Please login again.'}), 401
        
        # Find comment
        comment_obj = session_manager.query(comment).filter_by(ID=ID).first()
        if not comment_obj:
            return jsonify({"message": "Comment not found"}), 404
        
        # Check if user owns this comment
        if comment_obj.comment_by != session['user']:
            return jsonify({"message": "You don't have permission to update this comment"}), 403
        
        # Get new content
        new_comment_content = request.form.get('comment_content')
        if not new_comment_content:
            return jsonify({"message": "Comment content is required"}), 400
        
        # Update comment
        comment_obj.comment_content = new_comment_content
        comment_obj.update_at = datetime.now()
        session_manager.commit()
        
        return jsonify({
            "message": "Comment was updated successfully",
            "comment": {
                "id": comment_obj.ID,
                "content": comment_obj.comment_content,
                "updated_at": comment_obj.update_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error in update_comment: {e}")
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the exception(error): {e}')
        return jsonify({'message': 'An error occurred while updating comment'}), 500
    finally:
        session_manager.close()


@auth_view.route("/api/comment/reply/<string:comment_id>", methods=['POST'])
def reply_to_comment(comment_id):
    """
    Add a reply to a comment
    """
    session_manager = Session()
    try:
        # Check if user is logged in
        if 'user' not in session or 'session_id' not in session:
            return jsonify({"message": "Please login first"}), 401
        
        if not SESSION(session.get('user'), 'check', session.get('session_id')):
            return jsonify({'message': 'Invalid session. Please login again.'}), 401
        
        # Check if the parent comment exists
        parent_comment = session_manager.query(comment).filter_by(ID=comment_id).first()
        if not parent_comment:
            return jsonify({"message": "Comment not found"}), 404
        
        # Get form data
        reply_content = request.form.get('reply_content')
        reply_to_user = session['user']
        
        if not reply_content:
            return jsonify({"message": "Reply content is required"}), 400
        
        # Create reply - REMOVED link_id
        reply_obj = comment_reply(
            ID=config.ID(),
            comment_ID=comment_id,
            replay_content=reply_content,
            reply_comnntent_to=reply_to_user,
            create_at=datetime.now(),
            update_at=datetime.now()
        )
        session_manager.add(reply_obj)
        session_manager.commit()
        
        return jsonify({
            "message": "Reply was added successfully",
            "reply": {
                "id": reply_obj.ID,
                "content": reply_obj.replay_content,
                "by": reply_obj.reply_comnntent_to,
                "created_at": reply_obj.create_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error in reply_to_comment: {e}")
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the exception(error): {e}')
        return jsonify({'message': 'An error occurred while posting reply'}), 500
    finally:
        session_manager.close()


@auth_view.route("/api/comment/update_reply/<string:ID>", methods=['POST'])  # Added methods=['POST']
def update_comment_reply(ID):
    """
    Update a reply
    """
    session_manager = Session()
    try:
        # Check if user is logged in
        if 'user' not in session or 'session_id' not in session:
            return jsonify({"message": "Please login first"}), 401
        
        if not SESSION(session.get('user'), 'check', session.get('session_id')):
            return jsonify({'message': 'Invalid session. Please login again.'}), 401
        
        # Find reply
        reply_obj = session_manager.query(comment_reply).filter_by(ID=ID).first()
        if not reply_obj:
            return jsonify({"message": "Reply not found"}), 404
        
        # Check if user owns this reply
        if reply_obj.reply_comnntent_to != session['user']:
            return jsonify({"message": "You don't have permission to update this reply"}), 403
        
        # Get new content
        new_reply_content = request.form.get('reply_content')
        if not new_reply_content:
            return jsonify({"message": "Reply content is required"}), 400
        
        # Update reply
        reply_obj.replay_content = new_reply_content
        reply_obj.update_at = datetime.now()
        session_manager.commit()
        
        return jsonify({
            "message": "Reply was updated successfully",
            "reply": {
                "id": reply_obj.ID,
                "content": reply_obj.replay_content,
                "updated_at": reply_obj.update_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error in update_comment_reply: {e}")
        print(traceback.format_exc())
        config.log(f'[Error] : {request.endpoint} the exception(error): {e}')
        return jsonify({'message': 'An error occurred while updating reply'}), 500
    finally:
        session_manager.close()




@auth_view.route("/api/comments/<string:link_id>", methods=['GET'])
def get_comments(link_id):
    """
    Get all comments and replies for a specific link
    """
    session_manager = Session()
    try:
        # Get all comments for this link
        comments = session_manager.query(comment).filter_by(link_id=link_id).all()
        
        # Get all replies for these comments
        result = []
        for c in comments:
            replies = session_manager.query(comment_reply).filter_by(comment_ID=c.ID).all()
            result.append({
                "id": c.ID,
                "content": c.comment_content,
                "by": c.comment_by,
                "created_at": c.create_at.isoformat() if c.create_at else None,
                "updated_at": c.update_at.isoformat() if c.update_at else None,
                "replies": [{
                    "id": r.ID,
                    "content": r.replay_content,
                    "by": r.reply_comnntent_to,
                    "created_at": r.create_at.isoformat() if r.create_at else None,
                    "updated_at": r.update_at.isoformat() if r.update_at else None
                } for r in replies]
            })
        
        return jsonify({
            "link_id": link_id,
            "comments": result,
            "total": len(result)
        })
        
    except Exception as e:
        print(f"Error in get_comments: {e}")
        print(traceback.format_exc())
        return jsonify({'message': 'An error occurred while fetching comments'}), 500
    finally:
        session_manager.close()

