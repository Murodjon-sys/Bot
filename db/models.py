from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    language = Column(String, default='uz', nullable=False)  # uz, uz_cyrl, ru, en
    created_at = Column(DateTime, default=datetime.utcnow)
    trial_end = Column(DateTime, nullable=True)
    is_subscribed = Column(Boolean, default=False)
    subscription_plan = Column(String, nullable=True)  # 'basic' | 'premium' | None
    subscription_end = Column(DateTime, nullable=True)
    
    interests = relationship('UserInterest', back_populates='user', cascade='all, delete-orphan')

class UserInterest(Base):
    __tablename__ = 'user_interests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category = Column(String, nullable=False)
    
    user = relationship('User', back_populates='interests')

class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class News(Base):
    __tablename__ = 'news'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    message_id = Column(Integer)
    text = Column(Text)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_count = Column(Integer, default=0)
    
    # Media fields
    media_type = Column(String, nullable=True)  # 'photo' | 'video' | None
    media_file_id = Column(String, nullable=True)  # Telegram file_id (kichik media uchun)
    channel_username = Column(String, nullable=True)  # Forward uchun kanal username
    channel_message_id = Column(Integer, nullable=True)  # Forward uchun message ID
