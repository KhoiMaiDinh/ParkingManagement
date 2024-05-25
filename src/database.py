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
    CAR = "CAR"
    MOTORBIKE = "MOTORBIKE"
    
class CardTypeEnum(str, enum.Enum):
    MONTH="MONTH",
    DAY="DAY"
    
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(80), nullable=True)
    card_type = db.Column(db.Enum(CardTypeEnum))
    vehicle_type = db.Column(db.Enum(VehicleEnum))
    license_plate = db.Column(db.String(10), unique=True, nullable=True)
    uid = db.Column(db.String(10), unique=True, nullable=False)
    exp_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    
    # iohistories = db.relationship('IOHistory', backref="vehicle")
    
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self) -> str:
        return 'Vehicle>>> {self.license_plate}'
    
class IOEnum(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    

class IOHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(10), nullable=True)
    type = db.Column(db.Enum(IOEnum))
    img_url = db.Column(db.Text, nullable=False)
    crop_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self) -> str:
        return 'IOHistory>>> {self.vehicle_id}'