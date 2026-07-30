from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    bio = Column(Text)
    token = Column(String(100), nullable=True, unique=True)
    create_at = Column(DateTime,nullable=False)
    update_at = Column(DateTime,nullable=False)

    def __init__(self, username, display_name, email, password_hash, token, create_at=None, update_at=None, bio=None):
        self.username = username
        self.display_name = display_name
        self.email = email
        self.password_hash = password_hash
        self.bio = bio
        self.token = token
        self.create_at = create_at if create_at else datetime.now()
        self.update_at = update_at if update_at else datetime.now()

    def __repr__(self):
        return f"<User(username='{self.username}', display_name='{self.display_name}', email='{self.email}', token='{self.token}', create_at='{self.create_at}', update_at='{self.update_at}')>"

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

    ID = Column(String,primary_key=True)
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


