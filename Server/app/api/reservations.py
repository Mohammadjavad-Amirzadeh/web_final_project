from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.reservation import Reservation
from app.models.device import Device
from app.models.user import User
from app.utils.jwt_token_handler import verify_jwt_request
from datetime import datetime
import os
from sqlalchemy.exc import IntegrityError
import uuid

reservation_bp = Blueprint('reservation', __name__, url_prefix='/reservation')



@reservation_bp.route('/initiate', methods=['POST'])
def initiate_reservation():
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.form
    device_id_raw = data.get('device_id')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not device_id_raw or not start_time_str or not end_time_str:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        device_id = int(device_id_raw)
    except ValueError:
        return jsonify({'error': 'Invalid device_id'}), 400

    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404

    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use ISO format.'}), 400

    overlapping_reservation = Reservation.query.filter(
        Reservation.device_id == device.id,
        db.or_(
            Reservation.end_time == None,
            Reservation.end_time > start_time
        ),
        Reservation.start_time < (end_time or datetime.max)
    ).first()

    if overlapping_reservation:
        return jsonify({'error': 'Device is already reserved during this time'}), 409

    max_retries = 6
    for _ in range(max_retries):
        try:
            pending_id = str(uuid.uuid4())

            reservation = Reservation(
                user_id=user.id,
                device_id=device.id,
                start_time=start_time,
                end_time=end_time,
                is_free_mode=False,
                is_paid=False,
                upfront_paid=False,
                created_at=datetime.utcnow(),
                pending_id=pending_id
            )

            db.session.add(reservation)
            db.session.commit()

            return jsonify({
                'message': 'This reservation is pending for payment. Please proceed to payment. It will expire in 15 minutes.',
                'reservation_id': reservation.id,
                'pending_id': reservation.pending_id
            }), 201

        except IntegrityError:
            db.session.rollback()
            continue 

    return jsonify({'error': 'Could not create a unique pending reservation. Please try again.'}), 500
    
@reservation_bp.route('/half-payment/<string:pending_id>', methods=['PATCH'])
def confirm_half_payment(pending_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    reservation = Reservation.query.filter_by(pending_id=pending_id).first()
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    if reservation.user_id != payload.get("user_id"):
        return jsonify({"error": "not found"}), 404

    if reservation.is_paid:
        return jsonify({'error': 'Reservation is already paid'}), 400
    
    if reservation.upfront_paid:
        return jsonify({'error': 'Reservation is already half paid'}), 400
    
    reservation.half_completed_id = str(uuid.uuid4())
    reservation.half_paid_at = datetime.utcnow()
    reservation.confirmed_at = datetime.utcnow()
    reservation.upfront_paid = True
    db.session.commit()

    return jsonify({
        'message': 'Half payment confirmed, Reservation is now active',
        'reservation_id': reservation.id,
        'half_completed_id': reservation.half_completed_id
    }), 200

@reservation_bp.route('/complete-payment/<string:id>', methods=['PATCH'])
def confirm_full_payment(id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    reservation = Reservation.query.filter(
        db.or_(
            Reservation.half_completed_id == id,
            Reservation.pending_id == id)).first()
    
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    if reservation.user_id != payload.get("user_id"):
        return jsonify({"error": "not found"}), 404
    
    if reservation.is_paid:
        return jsonify({'error': 'Reservation is already paid'}), 400
    

    reservation.completed_id = str(uuid.uuid4())
    reservation.fully_paid_at = datetime.utcnow()
    reservation.confirmed_at = datetime.utcnow()
    reservation.is_paid = True
    db.session.commit()

    return jsonify({
        'message': 'Full payment confirmed, Reservation is now active',
        'reservation_id': reservation.id,
        'completed_id': reservation.completed_id
    }), 200

@reservation_bp.route('/device/<int:device_id>', methods=['GET'])
def get_reservations_of_device(device_id):
    reservations = Reservation.query.filter_by(device_id=device_id).all()
    if not reservations:
        return jsonify({'error': 'No reservations found for this device'}), 404

    reservations_list = []
    for reservation in reservations:
        reservations_list.append({
            'id': reservation.id,
            'user_id': reservation.user_id,
            'device_id': reservation.device_id,
            'start_time': reservation.start_time.isoformat(),
            'end_time': reservation.end_time.isoformat() if reservation.end_time else None,
            'is_free_mode': reservation.is_free_mode,
            'is_paid': reservation.is_paid,
            'upfront_paid': reservation.upfront_paid
        })
    return jsonify(reservations_list), 200


@reservation_bp.route('/reserve/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    payload, error_response, status_code = verify_jwt_request(request=request)
    if error_response:
        return error_response, status_code

    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user or not getattr(user, 'is_admin', False):
        return jsonify({"error": "Permission denied. Admins only."}), 403
    
    
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    return jsonify({
        'id': reservation.id,
        'user_id': reservation.user_id,
        'device_id': reservation.device_id,
        'start_time': reservation.start_time.isoformat(),
        'end_time': reservation.end_time.isoformat() if reservation.end_time else None,
        'is_free_mode': reservation.is_free_mode,
        'is_paid': reservation.is_paid,
        'upfront_paid': reservation.upfront_paid,
        'pending_id': reservation.pending_id,
        'half_completed_id': reservation.half_completed_id,
        'completed_id': reservation.completed_id,
    }), 200
