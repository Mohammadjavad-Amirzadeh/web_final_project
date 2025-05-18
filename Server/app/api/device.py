from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.device import Device
from app.models.user import User
import os
from werkzeug.utils import secure_filename
from app.utils.jwt_token_handler import verify_jwt_request

device_bp = Blueprint('device', __name__, url_prefix='/device')

@device_bp.route('/all', methods=['GET'])
def get_all_devices():
    devices = Device.query.all()
    return jsonify({
        "devices": [
            {
                "id": device.id,
                "name": device.name,
                "device_type": device.device_type.value,
                "hourly_rate": device.hourly_rate,
                "free_mode_rate": device.free_mode_rate,
                "is_available": device.is_available,
                "picture_url": device.picture_url
            }
            for device in devices
        ]
    }), 200
    
@device_bp.route('/<int:device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.get_or_404(device_id)
    return jsonify({
        "id": device.id,
        "name": device.name,
        "device_type": device.device_type.value,
        "hourly_rate": device.hourly_rate,
        "free_mode_rate": device.free_mode_rate,
        "is_available": device.is_available,
        "picture_url": device.picture_url
    }), 200

@device_bp.route('/add', methods=['POST'])
def add_device():
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied. Admins only."}), 403

    name = request.form.get('name')
    device_type = request.form.get('device_type')
    hourly_rate = request.form.get('hourly_rate')
    free_mode_rate = request.form.get('free_mode_rate')
    is_available = request.form.get('is_available', True)
    picture = request.files.get('picture')

    picture_url = "/static/uploads/images/default_device.png"
    upload_path = os.path.join("static", "uploads", "images")
    if picture:
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        filename = secure_filename(picture.filename)
        filepath = os.path.join(upload_path, filename)
        picture.save(filepath)
        picture_url = f"/static/uploads/images/{filename}"

    new_device = Device(
        name=name,
        device_type=device_type,
        hourly_rate=float(hourly_rate),
        free_mode_rate=float(free_mode_rate) if free_mode_rate else None,
        is_available=is_available in ['true', 'True', True, '1'],
        picture_url=picture_url
    )

    db.session.add(new_device)
    db.session.commit()

    return jsonify({
        "message": "Device added successfully",
        "device_id": new_device.id,
        "picture_url": picture_url
    }), 201

    
@device_bp.route('/update/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied. Admins only."}), 403
    
    device = Device.query.get(device_id)
    if device:
        name = request.form.get('name', device.name)
        device_type = request.form.get('device_type', device.device_type)
        hourly_rate = request.form.get('hourly_rate', device.hourly_rate)
        free_mode_rate = request.form.get('free_mode_rate', device.free_mode_rate)
        is_available = request.form.get('is_available')
        picture = request.files.get('picture')

        device.name = name
        device.device_type = device_type
        device.hourly_rate = float(hourly_rate) if hourly_rate else device.hourly_rate
        device.free_mode_rate = float(free_mode_rate) if free_mode_rate else device.free_mode_rate
        if is_available is not None:
            device.is_available = is_available in ['true', 'True', True, '1']

        if picture:
            upload_path = 'static/uploads/images'
            os.makedirs(upload_path, exist_ok=True)
            filename = secure_filename(picture.filename)
            filepath = os.path.join(upload_path, filename)
            picture.save(filepath)
            device.picture_url = f"/static/uploads/images/{filename}"

        db.session.commit()

        return jsonify({
            "message": "Device updated successfully",
            "device_id": device.id,
            "picture_url": device.picture_url
        }), 200
    else:
        return jsonify({
            "error": "Device not found"
        }), 404

@device_bp.route('/delete/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied. Admins only."}), 403
    
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({
            "message": "Device deleted successfully"
        }), 200
    else:
        return jsonify({
            "error": "Device not found"
        }), 404