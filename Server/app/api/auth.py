from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User, UserType
from app.models.email_verification import VerificationCode  
from sqlalchemy.exc import IntegrityError
from app.utils.code import generate_verification_code
from app.utils.send_email import send_verification_code
from dotenv import load_dotenv
import os
from app.utils.jwt_token_handler import generate_jwt

load_dotenv()

EXPIRATION_VERIFICATION_CODE_TIME = int(os.getenv("EXPIRATION_VERIFICATION_CODE_TIME")) 

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.password == password:
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.email_verified:
        return jsonify({"error": "Email is not verified"}), 403

    token = generate_jwt(user.id, user.email)

    return jsonify({
        "message": "Login successful",
        "token": token,
    }), 200

@auth_bp.route('/signup', methods=['POST'])
def signup():
    full_name = request.form.get('full_name')
    phone_number = request.form.get('phone_number')
    email = request.form.get('email') or None
    user_type = request.form.get('user_type', 'normal')
    password = request.form.get('password')

    if not full_name:
        return jsonify({"error": "Full name is required"}), 400

    try:
        code = generate_verification_code()

        user = User(
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            user_type=UserType(user_type.lower()),
            password=password,
            email_verified=False,
        )
        db.session.add(user)
        db.session.commit()  

        verification_code = VerificationCode(
            user_id=user.id,
            email=email,
            code=code,
            expire_time=datetime.utcnow() + timedelta(seconds=EXPIRATION_VERIFICATION_CODE_TIME)
        )
        db.session.add(verification_code)
        db.session.commit()

        send_verification_code(email, code)

        return jsonify({
            "message": "User created successfully",
            "user_id": user.id,
            'time': datetime.utcnow(),
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except ValueError:
        return jsonify({"error": f"'{user_type}' is not a valid user_type. Use: normal, subscriber, vip"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    email = request.form.get('email')
    code = request.form.get('code')

    if not email or not code:
        return jsonify({"error": "email and code are required"}), 400

    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        verification = VerificationCode.query.filter_by(user_id=user.id, code=code).first()

        if not verification:
            return jsonify({"error": "Invalid code or email"}), 404

        if verification.expire_time < datetime.utcnow():
            # db.session.delete(verification)
            # db.session.commit()
            return jsonify({"error": "Code has expired"}), 410

        user.email_verified = True
        db.session.delete(verification)
        db.session.commit()

        return jsonify({"message": "Email verified successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/resend-code', methods=['POST'])
def resend_verification_code():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.password != password:
            return jsonify({"error": "Invalid credentials"}), 401

        if user.email_verified:
            return jsonify({"message": "Email is already verified"}), 200

        VerificationCode.query.filter_by(user_id=user.id).delete()

        new_code = generate_verification_code()
        verification_code = VerificationCode(
            user_id=user.id,
            email=user.email,
            code=new_code,
            expire_time=datetime.utcnow() + timedelta(seconds=EXPIRATION_VERIFICATION_CODE_TIME)
        )

        db.session.add(verification_code)
        db.session.commit()

        send_verification_code(user.email, new_code)

        return jsonify({"message": "Verification code resent successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
