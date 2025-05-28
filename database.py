from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from utils import check_password, hash_password
import os

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
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    # Optional relationship (if you want to use it later)
    passwords = relationship("Password", back_populates="users", cascade="all, delete-orphan")


# Define Password model
class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True, autoincrement=True)
    website = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    profile = Column(Integer, ForeignKey('users.id'))

    users = relationship("User", back_populates="passwords")

def create_tables():
    Base.metadata.create_all(engine)

# Database class to handle database operations and session management.
class Database:
    current_user: User | None = None

    def __init__(self):
        # Define Session
        self.session = Session()

    def add_user(self, new_user):
        if self.session.query(User).filter_by(username=new_user.username).first():
            raise ValueError("Username already exists.")
        try:
            new_user.password = hash_password(new_user.password)
            self.session.add(new_user)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def verify_user(self, username, password):
        user = self.session.query(User).filter_by(username=username).first()
        if user and check_password(password, user.password):
            Database.current_user = user
            return user
        return None

    def get_all_passwords(self):
        return self.session.query(Password).all()

    def get_entry_by_website_and_username(self, website, username):
        return self.session.query(Password).filter_by(website=website, username=username).first()

    def add_password_entry(self, entry):
        try:
            self.session.add(entry)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def delete_password_by_id(self, entry_id):
        try:
            entry = self.session.query(Password).get(entry_id)
            if entry:
                self.session.delete(entry)
                self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def update_password_entry(self, entry_id, new_website, new_username, new_password):
        try:
            entry = self.session.query(Password).get(entry_id)
            if not entry:
                raise ValueError("Password entry not found.")

            if new_website:
                entry.website = new_website
            if new_username:
                entry.username = new_username
            if new_password:
                entry.password = new_password  # Use hash_password(new_password) if needed

            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise


    def close(self):
        if self.session:
            self.session.close()