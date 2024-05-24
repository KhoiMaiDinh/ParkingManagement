from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Card, IOHistory, IOEnum, db
from flasgger import swag_from
from src.plate_detector.detector import Model
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from cloudinary import uploader
import cloudinary.api
from cloudinary.utils import cloudinary
from io import BytesIO
import os
from datetime import datetime



car_parking = Blueprint("Card", __name__, url_prefix="/api/v1/card")

@car_parking.get("/")
@swag_from('../docs/car_parking/get_all.yaml')
# @jwt_required()
def get_vehicles():
    cards = Card.query.all()
    
    cardsDict = []

    # Iterate through the IOlist and extract the data into the format of array of lists
    for item in cards:
        vehicle_data = item.toDict()
        cardsDict.append(vehicle_data)
    return jsonify({
        'cards': cardsDict

    }), HTTP_200_OK

@car_parking.post("/")
@swag_from('../docs/car_parking/register.yaml')
# @jwt_required()
def register_new_vehicle():
    # try:
    owner_name = request.json['owner_name']
    license_plate = request.json['license_plate']
    uid = request.json['uid']
    exp_date = request.json['exp_date']
    vehicle_type = request.json['vehicle_type']
    card_type = request.json['card_type']
    exp_date_transformed = datetime.fromisoformat(exp_date)
    
    check_card = Card.query.filter(or_(uid==uid, license_plate==license_plate)).first()
    if check_card and check_card.uid == uid:
        return jsonify({
        'message': "card with same UID already registered"

    }), HTTP_409_CONFLICT
        
    if check_card and check_card.license_plate == license_plate:
        return jsonify({
        'message': "card with same plate number already registered"

    }), HTTP_409_CONFLICT
    
    
    card = Card(owner_name=owner_name, license_plate=license_plate, uid=uid, exp_date=exp_date_transformed, vehicle_type=vehicle_type, card_type = card_type)
    db.session.add(card)
    db.session.commit()
    return jsonify({
        'card': card.toDict()

    }), HTTP_201_CREATED
    
@car_parking.put("/<int:id>")
@swag_from('../docs/car_parking/edit.yaml')
# @jwt_required()
def edit_vehicle(id):
    owner_name = request.json['owner_name']
    license_plate = request.json['license_plate']
    uid = request.json['uid']
    exp_date = request.json['exp_date']
    vehicle_type = request.json['vehicle_type']
    card_type = request.json['card_type']
    exp_date_transformed = datetime.fromisoformat(exp_date)
    
    check_card = Card.query.filter(Card.id != id, or_(Card.uid == uid, Card.license_plate == license_plate)).first()
    if check_card and check_card.uid == uid:
        return jsonify({
        'message': "card with same UID already exist"

    }), HTTP_409_CONFLICT
        
    if check_card and check_card.license_plate == license_plate:
        return jsonify({
        'message': "card with same plate number already exist"

    }), HTTP_409_CONFLICT
    
    card = Card.query.filter_by(id=id).first()
    card.owner_name = owner_name
    card.license_plate = license_plate
    card.uid = uid
    card.exp_date = exp_date_transformed
    card.vehicle_type = vehicle_type
    card.card_type = card_type
    # db.session.add(vehicle)
    try:
        # Commit the changes
        db.session.commit()
        return jsonify({
            'card': card.toDict()
        }), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({
            'message': "Vehicle update failed",
            'error': f"Error: {e}"
        }), HTTP_400_BAD_REQUEST
    

    


