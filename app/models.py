from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer", nullable=False)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(30),
        default="OPEN",
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        default="MEDIUM",
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    technician_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        backref="service_requests"
    )

    technician = db.relationship(
        "User",
        foreign_keys=[technician_id],
        backref="assigned_requests"
    )

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.Text, nullable=False)

    service_request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    service_request = db.relationship(
        "ServiceRequest",
        backref="comments"
    )

    user = db.relationship(
        "User",
        backref="comments"
    )
class ActivityHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    action = db.Column(db.String(100), nullable=False)

    service_request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    service_request = db.relationship(
        "ServiceRequest",
        backref="activity_history"
    )

    user = db.relationship(
        "User",
        backref="activity_history"
    )