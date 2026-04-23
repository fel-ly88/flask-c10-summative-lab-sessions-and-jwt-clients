from config import db, bcrypt
from sqlalchemy.orm import validates

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    
    #a user has many workouts
    
    workouts = db.relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    
    @validates("username")
    def validate_username(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Username cannot be empty.")
        return value
    
    #hashes password on set, blocks reading raw password
    @property
    def password(self):
        raise AttributeError("Password is not readable.")
    
    @password.setter
    def password(self,plain_text):
        self._password_hash = bcrypt.generate_password_hash(plain_text).decode("utf-8")
        
    def authenticate(self,plain_text):
        return bcrypt.check_password_hash(self._password_hash, plain_text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }
        
class Workout(db.Model):
    __tablename__ = "workouts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    user = db.relationship("User", back_populates="workouts")
    
    def to_dict(self):
        return{
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "user_id": self.user_id
        }