import enum
from flask_sqlalchemy import SQLAlchemy, inspect
from datetime import datetime
import string
import random
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    # vehicles = db.relationship('Vehicle', backref="user")
    # bookmarks = db.relationship('Bookmark', backref="user")
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self) -> str:
        return 'User>>> {self.email}'
    
class VehicleEnum(str, enum.Enum):
    CAR = "car"
    MTB = "motorbike"
    
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(80), unique=True, nullable=True)
    vehicle_type = db.Column(db.Enum(VehicleEnum))
    license_plate = db.Column(db.String(10), unique=True, nullable=True)
    uid = db.Column(db.Integer, unique=True, nullable=False)
    exp_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    
    # iohistories = db.relationship('IOHistory', backref="vehicle")
    
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self) -> str:
        return 'Vehicle>>> {self.license_plate}'
    
class IOEnum(str, enum.Enum):
    IN = "in"
    OUT = "out"
    

class IOHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=True)
    type = db.Column(db.Enum(IOEnum))
    img_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self) -> str:
        return 'IOHistory>>> {self.vehicle_id}'
# class Bookmark(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text, nullable=True)
#     url = db.Column(db.Text, nullable=False)
#     short_url = db.Column(db.String(3), nullable=True)
#     visits = db.Column(db.Integer, default=0)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     created_at = db.Column(db.DateTime, default=datetime.now())
#     updated_at = db.Column(db.DateTime, onupdate=datetime.now())

#     def generate_short_characters(self):
#         characters = string.digits+string.ascii_letters
#         picked_chars = ''.join(random.choices(characters, k=3))

#         link = self.query.filter_by(short_url=picked_chars).first()

#         if link:
#             self.generate_short_characters()
#         else:
#             return picked_chars

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#         self.short_url = self.generate_short_characters()

#     def __repr__(self) -> str:
#         return 'Boomark>>> {self.url}'
