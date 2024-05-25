from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Card, IOHistory, IOEnum, CardTypeEnum, db
from flasgger import swag_from
from src.plate_detector.detector import Model, model
import pickle
import base64
import cloudinary
from cloudinary import uploader
import cloudinary.api
from cloudinary.utils import cloudinary
from io import BytesIO
import cv2
import urllib
import numpy as np
import os

def readFileFromUrl(link):
    req = urllib.urlopen(link)
    return req

def im2json(im):
        """Convert a Numpy array to JSON string"""
        imdata = pickle.dumps(im)
        jstr = base64.b64encode(imdata).decode('ascii')
        return jstr

in_out = Blueprint("in_out", __name__, url_prefix="/api/v1/in_out")
@in_out.post("/check_in")
@swag_from('../docs/in_out/check_in.yaml')
# @jwt_required()
def check_in():

    uploaded_image = request.files['image']
    uid = request.form.get('uid')
    copied_file = BytesIO(uploaded_image.getvalue())
    
    card = Card.query.filter_by(uid=uid).first()
    
    if not card:
        return jsonify({
            'message': "UID card has not been registered",
        }), HTTP_400_BAD_REQUEST
        
    last_ioHistory = IOHistory.query.filter_by(uid=uid).first()  
    
    if last_ioHistory and last_ioHistory.type == IOEnum.IN:
            return jsonify({
                'message': "The vehicle with UID has already checked in",
            }), HTTP_400_BAD_REQUEST

    # model = Model()
    
    plate_list, crop_img_list = model.predict(uploaded_image)
    # print(plate_list[0])
    if (len(plate_list) == 0):
        return jsonify({
            'message': "No plate founded in the image",
        }), HTTP_404_NOT_FOUND
        
    if (len(plate_list) > 1):
        return jsonify({
            'message': "Image has more than one plate, please try again",
        }), HTTP_400_BAD_REQUEST 
        
    
    
    if card.owner_name is None:

        response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 500, "crop": "fill"}])
        
        cv2.imwrite("crop.jpg", crop_img_list[0])
        crop_response=cloudinary.uploader.upload(
        'crop.jpg',
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 200, "crop": "fill"}])
        os.remove('crop.jpg')
    
        img_url = response['eager'][0]['secure_url']
        crop_url = crop_response['eager'][0]['secure_url']
            
        newIn = IOHistory(uid=uid, type=IOEnum.IN, img_url=img_url, crop_url=crop_url)
        db.session.add(newIn)
        db.session.commit()
        
        return jsonify({
            "id": newIn.id,
            "uid": card.uid,
            "card_type": card.card_type,
            "vehicle_type": card.vehicle_type,
            "img_url": newIn.img_url,
            "crop_url": newIn.crop_url,
            "created_at": newIn.created_at,
            "type": newIn.type
    }), HTTP_200_OK
    
    print(str(list(plate_list)[0]))
    isMatch = str(list(plate_list)[0]) == card.license_plate
    
    if (isMatch !=True):
        return jsonify({
        'message': "Plate number of the current vehicle is not the same with the one registered in card"
    }), HTTP_409_CONFLICT
    
    if not last_ioHistory or last_ioHistory.type == IOEnum.OUT:
        response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 500, "crop": "fill"}])
        
        cv2.imwrite("crop.jpg", crop_img_list[0])
        crop_response=cloudinary.uploader.upload(
        'crop.jpg',
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 200, "crop": "fill"}])
        os.remove('crop.jpg')
    
        img_url = response['eager'][0]['secure_url']
        crop_url = crop_response['eager'][0]['secure_url']
            
        newIn = IOHistory(uid=uid, type=IOEnum.IN, img_url=img_url, crop_url=crop_url)
        db.session.add(newIn)
        db.session.commit()
        
        return jsonify({
            "id": newIn.id,
            "uid": card.uid,
            "card_type": card.card_type,
            "vehicle_type": card.vehicle_type,
            "img_url": newIn.img_url,
            "crop_url": newIn.crop_url,
            "created_at": newIn.created_at,
            "type": newIn.type
    }), HTTP_200_OK

@in_out.post("/check_out")
@swag_from('../docs/in_out/check_out.yaml')
def check_out():

    uploaded_image = request.files['image']
    uid = request.form.get('uid')
    copied_file = BytesIO(uploaded_image.getvalue())
    
    card = Card.query.filter_by(uid=uid).first()
    
    if not card:
        return jsonify({
            'message': "UID card has not been registered",
        }), HTTP_400_BAD_REQUEST
        
    last_ioHistory = IOHistory.query.filter_by(uid=uid).first() 
    
    if not last_ioHistory or last_ioHistory.type == IOEnum.OUT:
        return jsonify({
                'message': "The vehicle with UID has not checked in, so we can't check out",
            }), HTTP_400_BAD_REQUEST

    # model = Model()
    
    plate_list, crop_img_list = model.predict(uploaded_image)
    # print(plate_list[0])
    if (len(plate_list) == 0):
        return jsonify({
            'message': "No plate founded in the image",
        }), HTTP_404_NOT_FOUND
        
    if (len(plate_list) > 1):
        return jsonify({
            'message': "Image has more than one plate, please try again",
        }), HTTP_400_BAD_REQUEST 
        
    if card.owner_name is None:
        last_ci_img = readFileFromUrl(last_ioHistory.img_url)    
        last_plate_list = model.predict(last_ci_img)    
        isMatch = str(list(plate_list)[0]) == str(list(last_plate_list)[0])
        
        if isMatch != True:
            return jsonify({
                'message': "Plate number of the current vehicle is not the same with the one of check in"
            }), HTTP_409_CONFLICT

        response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 500, "crop": "fill"}])
        
        cv2.imwrite("crop.jpg", crop_img_list[0])
        crop_response=cloudinary.uploader.upload(
        'crop.jpg',
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 200, "crop": "fill"}])
        os.remove('crop.jpg')
    
        img_url = response['eager'][0]['secure_url']
        crop_url = crop_response['eager'][0]['secure_url']
            
        newOut = IOHistory(uid=uid, type=IOEnum.OUT, img_url=img_url, crop_url=crop_url)
        db.session.add(newOut)
        db.session.commit()
        
        return jsonify({
            "id": newOut.id,
            "uid": card.uid,
            "card_type": card.card_type,
            "vehicle_type": card.vehicle_type,
            "img_url": newOut.img_url,
            "crop_url": newOut.crop_url,
            "created_at": newOut.created_at,
            "type": newOut.type
        }), HTTP_200_OK
    
    print(str(list(plate_list)[0]))
    isMatch = str(list(plate_list)[0]) == card.license_plate
    
    if (isMatch !=True):
        return jsonify({
        'message': "Plate number of the current vehicle is not the same with the one registered in card"
    }), HTTP_409_CONFLICT
    
    if last_ioHistory.type == IOEnum.IN:
        response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 500, "crop": "fill"}])
        
        cv2.imwrite("crop.jpg", crop_img_list[0])
        crop_response=cloudinary.uploader.upload(
        'crop.jpg',
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 200, "crop": "fill"}])
        # os.remove('crop.jpg')
    
        img_url = response['eager'][0]['secure_url']
        crop_url = crop_response['eager'][0]['secure_url']
            
        newOut = IOHistory(uid=uid, type=IOEnum.OUT, img_url=img_url, crop_url=crop_url)
        db.session.add(newOut)
        db.session.commit()
        
        return jsonify({
            "id": newOut.id,
            "uid": card.uid,
            "card_type": card.card_type,
            "vehicle_type": card.vehicle_type,
            "img_url": newOut.img_url,
            "crop_url": newOut.crop_url,
            "created_at": newOut.created_at,
            "type": newOut.type
    }), HTTP_200_OK
        
@in_out.get("/<int:id>")
@swag_from('../docs/in_out/get_by_card_id.yaml')
# @jwt_required()
def getIOofID(id):
    IOlist = IOHistory.query.filter_by(uid=id)
    
    IOdict = []
    for item in IOlist:
        io_data = item.toDict()
        IOdict.append(io_data)
    
    return jsonify({'io_list': IOdict})

@in_out.delete("/all_io")
@swag_from('../docs/in_out/delete_all.yaml')
# @jwt_required()
def deleteAllIO():
    try:
        num_rows_deleted = db.session.query(IOHistory).delete()
        db.session.commit()
    except:
        db.session.rollback()
    
    return jsonify({'message': 'All records deleted'})

@in_out.get("/all_io")
@swag_from('../docs/in_out/get_all.yaml')
# @jwt_required()
def getAllIO():
    IOlist = IOHistory.query.all()
    
    IODist = []

    # Iterate through the IOlist and extract the data into the format of array of lists
    for item in IOlist:
        card = Card.query.filter_by(uid=item.uid).first()
        if card is None: continue
        IODist.append({
            "id": item.id,
            "uid": item.uid,
            "card_type": card.card_type,
            "vehicle_type": card.vehicle_type,
            "img_url": item.img_url,
            "crop_url": item.crop_url,
            "created_at": item.created_at,
            "type": item.type
        })
    return jsonify({
        'io_list': IODist
    }), HTTP_200_OK
