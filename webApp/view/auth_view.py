from flask import Blueprint, render_template, request, redirect, url_for, session

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
    session_manger = Session()
    if 'user' not in session:
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

