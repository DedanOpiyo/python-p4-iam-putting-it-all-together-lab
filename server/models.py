from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
# import validators # pipenv install v

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user_id','-recipes.user',) # Tuple
    serialize_only = ('id', 'username', 'image_url', 'bio', 'recipes',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationship(s)
    recipes = db.relationship('Recipe', back_populates='user')

    @hybrid_property # hybrid_property ?
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8') # utf-8 ?
        )
        self._password_hash = password_hash.decode('utf-8')
    
    # Any appropriate decorator ?
    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )
    
    @classmethod
    def create(cls, username, password, image_url=None, bio=None):
        user = cls(
            username=username,
            image_url=image_url,
            bio=bio
        )
        user.password_hash = password # Still respecting privacy & upholding encapsulation
        return user
    
    def __repr__(self):
        return f"User ID: {self.id}, username: {self.username}, bio:{self.bio}, image_url: {self.image_url}"

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    serialize_rules = ('-user.recipes',) # Tuple # '-user_id',
    serialize_only = ('id', 'title', 'instructions', 'minutes_to_complete', 'user_id', 'user',)

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    # FK
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationship(s)
    user = db.relationship('User', back_populates='recipes')

    # Validations
    @validates('instructions')
    def validate_instructions(self, key, value):
        if not value and len(value) < 50:
            raise ValueError('Recipe instructions should be at least 50 characters long.')
        return value