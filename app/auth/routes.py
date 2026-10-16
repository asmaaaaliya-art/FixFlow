from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity,create_access_token
from werkzeug.security import generate_password_hash, check_password_hash


from app.models import db, User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    hashed_password = generate_password_hash(password)

    user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

   
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route("/create-technician", methods=["POST"])
@jwt_required()
def create_technician():
    admin_id = get_jwt_identity()
    admin = db.session.get(User, int(admin_id))

    if not admin or admin.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    technician = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role="technician"
    )

    db.session.add(technician)
    db.session.commit()

    return jsonify({
        "message": "Technician created successfully",
        "user_id": technician.id,
        "name": technician.name,
        "email": technician.email,
        "role": technician.role
    }), 201

@auth_bp.route("/create-technicians-bulk", methods=["POST"])
@jwt_required()
def create_technicians_bulk():
    admin_id = get_jwt_identity()
    admin = db.session.get(User, int(admin_id))

    if not admin or admin.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}
    technicians = data.get("technicians")

    if not isinstance(technicians, list) or not technicians:
        return jsonify({
            "error": "A non-empty technicians list is required"
        }), 400

    created = []
    skipped = []

    try:
        for item in technicians:
            if not isinstance(item, dict):
                skipped.append({"reason": "Invalid technician data"})
                continue

            name = item.get("name")
            email = item.get("email")
            password = item.get("password")

            if not name or not email or not password:
                skipped.append({
                    "email": email,
                    "reason": "Name, email and password are required"
                })
                continue

            if User.query.filter_by(email=email).first():
                skipped.append({
                    "email": email,
                    "reason": "Email already registered"
                })
                continue

            technician = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                role="technician"
            )

            db.session.add(technician)
            db.session.flush()

            created.append({
                "id": technician.id,
                "name": technician.name,
                "email": technician.email,
                "role": technician.role
            })

        db.session.commit()

    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Technician creation failed; no changes were saved"
        }), 500

    return jsonify({
        "message": "Bulk technician creation completed",
        "created_count": len(created),
        "skipped_count": len(skipped),
        "created": created,
        "skipped": skipped
    }), 201
