from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import db, ServiceRequest,User, Comment,ActivityHistory


request_bp = Blueprint(
    "service_requests",
    __name__,
    url_prefix="/requests"
)


@request_bp.route("/", methods=["POST"])
@jwt_required()
def create_request():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "MEDIUM")

    if not title or not description:
        return jsonify({
            "error": "Title and description are required"
        }), 400

    user_id = get_jwt_identity()

    new_request = ServiceRequest(
    title=title,
    description=description,
    priority=priority,
    customer_id=int(user_id)
)

    db.session.add(new_request)
    db.session.flush()

    activity = ActivityHistory(
    action="Service request created",
    service_request_id=new_request.id,
    user_id=int(user_id)
)

    db.session.add(activity)
    db.session.commit()

    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        "message": "Service request created successfully",
        "request_id": new_request.id
    }), 201


@request_bp.route("/", methods=["GET"])
@jwt_required()
def get_my_requests():

    user_id = get_jwt_identity()

    requests = ServiceRequest.query.filter_by(
        customer_id=int(user_id)
    ).all()

    result = []

    for service_request in requests:
        result.append({
            "id": service_request.id,
            "title": service_request.title,
            "description": service_request.description,
            "status": service_request.status,
            "priority": service_request.priority
        })

    return jsonify({
        "requests": result
    }), 200

@request_bp.route("/admin", methods=["GET"])
@jwt_required()
def get_all_requests():

    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user.role != "admin":
        return jsonify({
            "error": "Admin access required"
        }), 403

    status = request.args.get("status")
    priority = request.args.get("priority")
    search = request.args.get("search")
    sort = request.args.get("sort")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    query = ServiceRequest.query

    if status:
        query = query.filter_by(status=status)

    if priority:
        query = query.filter_by(priority=priority)
    if search:
     query = query.filter(
        ServiceRequest.title.ilike(f"%{search}%")
    )

    if sort == "newest":
     query = query.order_by(ServiceRequest.id.desc())

    elif sort == "oldest":
     query = query.order_by(ServiceRequest.id.asc())

    pagination = query.paginate(
    page=page,
    per_page=per_page,
    error_out=False
)

    requests = pagination.items 
   

    result = []

    for service_request in requests:
        result.append({
            "id": service_request.id,
            "title": service_request.title,
            "description": service_request.description,
            "status": service_request.status,
            "priority": service_request.priority,
            "customer_id": service_request.customer_id,
            "technician_id": service_request.technician_id
        })

    return jsonify({
    "requests": result,
    "page": pagination.page,
    "per_page": pagination.per_page,
    "total": pagination.total,
    "pages": pagination.pages
}), 200

@request_bp.route("/<int:request_id>/assign", methods=["PUT"])
@jwt_required()
def assign_technician(request_id):

    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if user.role != "admin":
        return jsonify({
            "error": "Admin access required"
        }), 403

    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({
            "error": "Service request not found"
        }), 404

    data = request.get_json()

    technician_id = data.get("technician_id")

    if not technician_id:
        return jsonify({
            "error": "technician_id is required"
        }), 400

    technician = User.query.get(technician_id)

    if not technician or technician.role != "technician":
        return jsonify({
            "error": "Valid technician not found"
        }), 404
    service_request.technician_id = technician.id
    service_request.status = "ASSIGNED"

    activity = ActivityHistory(
    action="Technician assigned",
    service_request_id=service_request.id,
    user_id=int(user_id)
)

    db.session.add(activity)
    db.session.commit()

    return jsonify({
        "message": "Technician assigned successfully",
        "request_id": service_request.id,
        "technician_id": technician.id,
        "status": service_request.status
    }), 200

@request_bp.route("/technician", methods=["GET"])
@jwt_required()
def get_technician_requests():

    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user or user.role != "technician":
        return jsonify({
            "error": "Technician access required"
        }), 403

    requests = ServiceRequest.query.filter_by(
        technician_id=int(user_id)
    ).all()

    result = []

    for service_request in requests:
        result.append({
            "id": service_request.id,
            "title": service_request.title,
            "status": service_request.status,
            "priority": service_request.priority
        })

    return jsonify({
        "requests": result
    }), 200

@request_bp.route("/<int:request_id>/status", methods=["PUT"])
@jwt_required()
def update_request_status(request_id):
    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))
    if not user or user.role != "technician":
        return jsonify({
              "error": "Technician access required"
        }), 403
    service_request = db.session.get(ServiceRequest, int(request_id))
    if not service_request:
        return jsonify({
            "error": "Service request not found"
        }), 404
    if service_request.technician_id != int(user_id):
         return jsonify({
            "error": "This request is not assigned to you"
        }), 403
    data = request.get_json(silent=True)
    if not data:
            return jsonify({
            "error": "JSON data is required"
        }), 400

    new_status = data.get("status")


    allowed_statuses = [
        "IN_PROGRESS",
        "RESOLVED"
    ]
    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status"
        }), 400
    service_request.status = new_status

    activity = ActivityHistory(
    action=f"Status changed to {new_status}",
    service_request_id=service_request.id,
    user_id=int(user_id)
)

    db.session.add(activity)
    db.session.commit()
    

    return jsonify({
        "message": "Request status updated successfully",
        "request_id": service_request.id,
        "status": service_request.status
    }), 200

@request_bp.route("/<int:request_id>/close", methods=["PUT"])
@jwt_required()
def close_request(request_id):
   user_id = get_jwt_identity()
   user = db.session.get(User, int(user_id))
   if not user or user.role != "customer":
        return jsonify({
            "error": "Customer access required"
        }), 403
   service_request = ServiceRequest.query.get(request_id)
   if not service_request:
        return jsonify({
            "error": "Service request not found"
        }), 404
   if service_request.customer_id != int(user_id):
        return jsonify({
            "error": "This request does not belong to you"
        }), 403
   if service_request.status != "RESOLVED":
        return jsonify({
            "error": "Only resolved requests can be closed"
        }), 400
   service_request.status = "CLOSED"

   activity = ActivityHistory(
    action="Service request closed",
    service_request_id=service_request.id,
    user_id=int(user_id)
)

   db.session.add(activity)
   db.session.commit()
   return jsonify({
        "message": "Service request closed successfully",
        "request_id": service_request.id,
        "status": service_request.status
    }), 200

@request_bp.route("/<int:request_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(request_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    service_request = db.session.get(ServiceRequest, request_id)

    if not service_request:
        return jsonify({"error": "Service request not found"}), 404

    if not can_access_request(user, service_request):
        return jsonify({"error": "You cannot comment on this request"}), 403

    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Comment message is required"}), 400

    comment = Comment(
        message=message,
        user_id=user_id,
        service_request_id=request_id
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": "Comment added successfully",
        "comment": {
            "id": comment.id,
            "message": comment.message,
            "user_id": comment.user_id,
            "user_name": user.name
        }
    }), 201


def can_access_request(user, service_request):
    if not user or not service_request:
        return False

    if user.role == "admin":
        return True

    if user.role == "customer":
        return service_request.customer_id == user.id

    if user.role == "technician":
        return service_request.technician_id == user.id

    return False


@request_bp.route("/<int:request_id>/comments", methods=["GET"])
@jwt_required()
def get_comments(request_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    service_request = db.session.get(ServiceRequest, request_id)

    if not service_request:
        return jsonify({"error": "Service request not found"}), 404

    if not can_access_request(user, service_request):
        return jsonify({"error": "You cannot access these comments"}), 403

    comments = Comment.query.filter_by(
        service_request_id=request_id
    ).all()

    result = []

    for comment in comments:
        result.append({
            "id": comment.id,
            "message": comment.message,
            "user_id": comment.user_id,
            "user_name": comment.user.name
        })

    return jsonify({
        "request_id": request_id,
        "comments": result
    }), 200


@request_bp.route("/<int:request_id>/activity", methods=["GET"])
@jwt_required()
def get_activity(request_id):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    service_request = db.session.get(ServiceRequest, request_id)

    if not service_request:
        return jsonify({"error": "Service request not found"}), 404

    if not can_access_request(user, service_request):
        return jsonify({"error": "You cannot access this activity"}), 403

    activities = ActivityHistory.query.filter_by(
        service_request_id=request_id
    ).all()

    result = []

    for activity in activities:
        result.append({
            "id": activity.id,
            "action": activity.action,
            "user_id": activity.user_id,
            "user_name": activity.user.name
        })

    return jsonify({
        "request_id": request_id,
        "activity": result
    }), 200