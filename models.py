import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Ensure the ./data directory exists
os.makedirs("data", exist_ok=True)

# Absolute path to the database file
db_path = os.path.abspath(os.path.join("data", "users.db"))

# Create SQLAlchemy engine
engine = create_engine(f"sqlite:///{db_path}", echo=False)

# Base class for ORM models
Base = declarative_base()

# Create a session factory
Session = sessionmaker(bind=engine)


# Define Users model
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    # Optional relationship (if you want to use it later)
    passwords = relationship("Passwords", back_populates="users", cascade="all, delete-orphan")


# Define Password model
class Passwords(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    website = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    profile = Column(Integer, ForeignKey('users.id'))

    users = relationship("Users", back_populates="passwords")


# Function to create all tables
def create_tables():
    Base.metadata.create_all(engine)
