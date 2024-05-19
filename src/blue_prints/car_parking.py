from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Card, IOHistory, IOEnum, db
from flasgger import swag_from
from src.plate_detector.detector import Model
from sqlalchemy.exc import IntegrityError
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
    vehicles = Card.query.all()
    
    vehicleDict = []

    # Iterate through the IOlist and extract the data into the format of array of lists
    for item in vehicles:
        vehicle_data = item.toDict()
        vehicleDict.append(vehicle_data)
    return jsonify({
        'Cards': vehicleDict

    }), HTTP_200_OK

@car_parking.post("/register")
@swag_from('../docs/car_parking/register.yaml')
# @jwt_required()
def register_new_vehicle():
    # try:
    owner_name = request.json['owner_name']
    license_plate = request.json['license_plate']
    uid = request.json['uid']
    exp_date = request.json['exp_date']
    vehicle_type = request.json['vehicle_type']
    exp_date_transformed = datetime.fromisoformat(exp_date)
    
    vehicle = Card(owner_name=owner_name, license_plate=license_plate, uid=uid, exp_date=exp_date_transformed, vehicle_type=vehicle_type)
    db.session.add(vehicle)
    db.session.commit()
    return jsonify({
        'message': "Vehicle registered",
        'vehicle': vehicle.toDict()

    }), HTTP_201_CREATED
    
@car_parking.put("/edit")
@swag_from('../docs/car_parking/edit.yaml')
# @jwt_required()
def edit_vehicle():
    id = request.json['id']
    owner_name = request.json['owner_name']
    license_plate = request.json['license_plate']
    uid = request.json['uid']
    exp_date = request.json['exp_date']
    vehicle_type = request.json['vehicle_type']
    exp_date_transformed = datetime.fromisoformat(exp_date)
    
    vehicle = Card.query.filter_by(id=id).first()
    vehicle.owner_name = owner_name
    vehicle.license_plate = license_plate
    vehicle.uid = uid
    vehicle.exp_date = exp_date_transformed
    vehicle.vehicle_type = vehicle_type
    # db.session.add(vehicle)
    try:
        # Commit the changes
        db.session.commit()
        return jsonify({
            'message': "Vehicle updated",
            'vehicle': vehicle.toDict()
        }), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({
            'message': "Vehicle update failed",
            'error': f"Error: {e}"
        }), HTTP_400_BAD_REQUEST
    

    


