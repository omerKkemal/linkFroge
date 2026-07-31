from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    bio = Column(Text)
    token = Column(String(100), nullable=True, unique=True)
    create_at = Column(DateTime,nullable=False)
    update_at = Column(DateTime,nullable=False)

    def __init__(self, id, username, display_name, email, password_hash, token, create_at=None, update_at=None, bio=None):
        self.id = id
        self.username = username
        self.display_name = display_name
        self.email = email
        self.password_hash = password_hash
        self.bio = bio
        self.token = token
        self.create_at = create_at if create_at else datetime.now()
        self.update_at = update_at if update_at else datetime.now()

    def __repr__(self):
        return f"<id={self.id} User(username='{self.username}', display_name='{self.display_name}', email='{self.email}', token='{self.token}', create_at='{self.create_at}', update_at='{self.update_at}')>"

class SESSION_LOGIN(Base):
    __tablename__ = 'SESSION'
    ID = Column(String, primary_key=True)
    username = Column(String(20), ForeignKey('users.username', ondelete="CASCADE"))
    session_id = Column(String(50))

    def __init__(self, ID, username, session_id):
        self.ID = ID
        self.username = username
        self.session_id = session_id

    def __repr__(self):
        return f"[{self.ID},{self.username},{self.session_id}]"

class service_linkes(Base):
    __tablename__ = "service_linkes"

    ID = Column(String,primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    service_link = Column(String,nullable=False, unique=True)
    status = Column(String,nullable=False, default='offline')
    visibility = Column(String,nullable=False)
    catagory = Column(String, nullable=False)
    create_at = Column(DateTime,nullable=False)
    update_at = Column(DateTime,nullable=False)


    def __init__(self, ID, user_id, service_link, visibility, catagory, status=None, create_at=None, update_at=None):
        self.ID = ID
        self.user_id = user_id
        self.service_link = service_link
        self.status = status if status else 'offline'
        self.visibility = visibility
        self.catagory = catagory
        self.create_at = create_at if create_at else datetime.now()
        self.update_at = update_at if update_at else datetime.now()
    def __repr__(self):
        return f"<service_linkes(ID='{self.ID}', user_id='{self.user_id}', service_link='{self.service_link}', catagory={self.catagory},status='{self.status}', visibility={self.visibility} ,create_at='{self.create_at}', update_at='{self.update_at}')>"

class comment(Base):
    __tablename__ = "comment"

    ID = Column(String, nullable=False, primary_key=True)
    comment_content = Column(String, nullable=False)
    link_id = Column(String, ForeignKey('service_linkes.ID', ondelete="CASCADE")) 
    comment_by = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False) # the owner of this comment can delelte or update
    create_at = Column(DateTime,nullable=False)
    update_at = Column(DateTime,nullable=False)

    def __init__(self, ID, comment_content, link_id, comment_by, create_at=None, update_at=None):
        self.ID = ID
        self.comment_content = comment_content
        self.link_id = link_id
        self.comment_by = comment_by
        self.create_at = create_at if create_at else datetime.now()
        self.update_at = update_at if update_at else datetime.now()

    def __repr__(self):
        return f"<comment_content={self.comment_content}, link_id={self.link_id}, comment_by={self.comment_by}, create_at={self.create_at}, update_at={self.update_at}>"

class comment_reply(Base):
    __tablename__ = "commant_reply"
    ID = Column(String, primary_key=True, nullable=False)
    comment_ID = Column(String, ForeignKey("comment.ID", ondelete="CASCADE"))
    replay_content = Column(String, nullable=False)
    reply_comnntent_to = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    create_at = Column(DateTime, nullable=False)
    update_at = Column(DateTime, nullable=False)

    def __init__(self, ID, comment_ID, replay_content, reply_comnntent_to, create_at=None, update_at=None):
        self.ID = ID
        self.comment_ID = comment_ID
        self.replay_content = replay_content
        self.reply_comnntent_to = reply_comnntent_to
        self.create_at = create_at if create_at else datetime.now()
        self.update_at = update_at if update_at else datetime.now()
    def __repr__(self):
        return f"<ID={self.ID}, comment_ID={self.comment_ID}, replay_content={self.replay_content}, reply_comnntent_to={self.reply_comnntent_to}, create_at={self.create_at}, update_at={self.update_at}>"
    



