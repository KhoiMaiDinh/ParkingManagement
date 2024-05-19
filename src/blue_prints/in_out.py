from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import Card, IOHistory, IOEnum, db
from flasgger import swag_from
from src.plate_detector.detector import Model
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
    

    # try:
    uploaded_image = request.files['image']
    uid = request.form.get('uid')
    copied_file = BytesIO(uploaded_image.getvalue())
    
    card = Card.query.filter_by(uid=uid).first()
    
    if not card:
        return jsonify({
            'message': "UID card has not been registered",
        }), HTTP_400_BAD_REQUEST
        
    # if card.owner_name is None:
        # last_ioHistory = IOHistory.query.filter_by(uid=uid).first()
        
        # if last_ioHistory.type == IOEnum.IN:
        #     return jsonify({
        #         'message': "The vehicle with UID has already checked in",
        #     }), HTTP_400_BAD_REQUEST
        


    
    model = Model()
    
    plate_list, crop_img = model.predict(uploaded_image)
    # print(plate_list[0])
    
    
    if (len(plate_list) == 0):
        return jsonify({
            'message': "No plate founded in the image",
        }), HTTP_404_NOT_FOUND
    # vehicle = Vehicle(owner_name=owner_name, register_by=register_by, license_plate=license_plate, uid=uid)
    # db.session.add(vehicle)
    # db.session.commit()
    if (len(plate_list) > 1):
        return jsonify({
            'message': "Image has more than one plate, please try again",
        }), HTTP_200_OK 
        
    last_ioHistory = IOHistory.query.filter_by(uid=uid).first()    
    
    if card.owner_name is None:
        if last_ioHistory.type == IOEnum.IN:
            return jsonify({
                'message': "The vehicle with UID has already checked in",
            }), HTTP_400_BAD_REQUEST
            
        response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 5300, "crop": "fill"}])
    
        img_url = response['eager'][0]['secure_url']
        print(img_url)
            
        newIn = IOHistory(uid=uid, type=IOEnum.IN, img_url=img_url)
        db.session.add(newIn)
        db.session.commit()
        
        return jsonify({
            'message': "Guess card please get inside",
            'card_info': card.toDict(),
            'crop_img': im2json(crop_img[0]),
            'history_record': newIn.toDict()
        }), HTTP_200_OK
    
    isMatch = str(list(plate_list)[0]) == card.license_plate
    
    if (isMatch !=True):
        return jsonify({
        'message': "Plate number of the current vehicle is not the same with the one registered in card"
    }), HTTP_200_OK
    
    
    
    response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 5300, "crop": "fill"}])
    
    img_url = response['eager'][0]['secure_url']
    print(img_url)
    
    
    
    if not last_ioHistory or last_ioHistory.type == IOEnum.OUT:
        newIn = IOHistory(uid=uid, type=IOEnum.IN, img_url=img_url)
        db.session.add(newIn)
        db.session.commit()
        
        return jsonify({
        'message': "Plate match, please get inside",
        'card_info': card.toDict(),
        'crop_img': im2json(crop_img[0]),
        'history_record': newIn.toDict()
    }), HTTP_200_OK
    else:
        return jsonify({
            'message': "The vehicle with UID has already checked in",
        }), HTTP_400_BAD_REQUEST
        
    #     newOut = IOHistory(uid = uid, type=IOEnum.OUT, img_url="http://test")
    #     db.session.add(newOut)
    #     db.session.commit()
        
    #     return jsonify({
    #     'message': "Plate match, please get outside",
    #     'card_info': card.toDict(),
    #     'crop_img': im2json(crop_img[0]),
    #     'history_record': newOut.toDict()
    # }), HTTP_200_OK

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
    
    model = Model()
    
    plate_list, crop_img = model.predict(uploaded_image)
    # print(plate_list[0])
    
    
    if (len(plate_list) == 0):
        return jsonify({
            'message': "No plate founded in the image",
        }), HTTP_404_NOT_FOUND

    if (len(plate_list) > 1):
        return jsonify({
            'message': "Image has more than one plate, please try again",
        }), HTTP_200_OK 
        
    last_ioHistory = IOHistory.query.filter_by(uid=uid).first()    
    
    if card.owner_name is None:
        if last_ioHistory.type == IOEnum.OUT:
            return jsonify({
                'message': "The vehicle with UID has already checked out",
            }), HTTP_400_BAD_REQUEST
        last_ci_img = readFileFromUrl(last_ioHistory.img_url)    
        last_plate_list = model.predict(last_ci_img)    
        isMatch = str(list(plate_list)[0]) == str(list(last_plate_list)[0])
            
        response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 500, "crop": "fill"}])
    
        img_url = response['eager'][0]['secure_url']
        print(img_url)
            
        newOut = IOHistory(uid=uid, type=IOEnum.OUT, img_url=img_url)
        db.session.add(newOut)
        db.session.commit()
        
        return jsonify({
            'message': "Guess card please get outside",
            'card_info': card.toDict(),
            'crop_img': im2json(crop_img[0]),
            'history_record': newOut.toDict()
        }), HTTP_200_OK
    
    isMatch = str(list(plate_list)[0]) == card.license_plate
    
    if (isMatch !=True):
        return jsonify({
        'message': "Plate number of the current vehicle is not the same with the one registered in card"
    }), HTTP_200_OK
    
    response=cloudinary.uploader.upload(
        copied_file,
        unique_filename = True, 
        overwrite=True,
        eager=[{"width": 500, "crop": "fill"}])
    
    img_url = response['eager'][0]['secure_url']
    print(img_url)
    
    
    
    if last_ioHistory and last_ioHistory.type == IOEnum.IN:
        newOut = IOHistory(uid=uid, type=IOEnum.OUT, img_url=img_url)
        db.session.add(newOut)
        db.session.commit()
        
        return jsonify({
        'message': "Plate match, please get outside",
        'card_info': card.toDict(),
        'crop_img': im2json(crop_img[0]),
        'history_record': newOut.toDict()
    }), HTTP_200_OK
    else:
        return jsonify({
            'message': "The vehicle with UID has already checked out",
        }), HTTP_400_BAD_REQUEST
        
@in_out.get("/<int:id>")
@swag_from('../docs/in_out/get_by_card_id.yaml')
# @jwt_required()
def getIOofID(id):
    IOlist = IOHistory.query.filter_by(uid=id)
    
    IOdict = []
    for item in IOlist:
        io_data = item.toDict()
        IOdict.append(io_data)
        
    if len(IOdict) == 0:
        return jsonify({'message': "No IO history founded with this UID"}), HTTP_404_NOT_FOUND
    
    return jsonify({'io_list': IOdict})

@in_out.delete("/all_io")
@swag_from('../docs/in_out/get_all.yaml')
# @jwt_required()
def deleteAllIO():
    try:
        num_rows_deleted = db.session.query(IOHistory).delete()
        db.session.commit()
    except:
        db.session.rollback()
    
    return jsonify({'message': 'All records deleted'})