from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)

class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    website = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)


    def __init__(self, website, username, password):
        self.website = website
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<Password(website='{self.website}', username='{self.username}')>"