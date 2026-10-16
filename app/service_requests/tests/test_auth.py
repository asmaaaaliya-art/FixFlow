from app import create_app
from app import db
import uuid
from app import create_app, db
from app.config import TestConfig


def test_home():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json["application"] == "FixFlow"

def test_register():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"pytest_{uuid.uuid4().hex}@test.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "test123"
        }
    )

    assert response.status_code == 201

def test_login():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"login_{uuid.uuid4().hex}@test.com"
    password = "test123"

    # Register a test user
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Login Test User",
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    # Log in with that user
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json

    def test_get_my_requests():
        app = create_app(TestConfig)
    client = app.test_client()

    response = client.get("/requests/")

    assert response.status_code == 401

    def test_login_wrong_password():
        app = create_app(TestConfig)
    client = app.test_client()

    response = client.post(
        "/auth/login",
        json={
            "email": "ahamed@test.com",
            "password": "wrong_password_123"
        }
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid email or password"

    def test_register_missing_fields():
        app = create_app(TestConfig)
    client = app.test_client()

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User"
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == (
        "Name, email and password are required"
    )
def test_get_requests_with_token():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"token_test_{uuid.uuid4().hex}@test.com"
    password = "test123"

    client.post(
        "/auth/register",
        json={
            "name": "Token Test User",
            "email": email,
            "password": password
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    token = login_response.json["access_token"]

    response = client.get(
        "/requests/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "requests" in response.json

def test_register_duplicate_email():
        app = create_app(TestConfig)
        client = app.test_client()

        email = f"duplicate_{uuid.uuid4().hex}@test.com"

        data = {
        "name": "Test User",
        "email": email,
        "password": "test123"
    }

    # Register the user once
        first_response = client.post(
        "/auth/register",
        json=data
    )

    # Try registering the same email again
        second_response = client.post(
        "/auth/register",
        json=data
    )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json["error"] == "Email already registered"

def test_login_unknown_email():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"unknown_{uuid.uuid4().hex}@test.com"

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test123"
        }
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid email or password"


def test_register_missing_password():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": f"missing_{uuid.uuid4().hex}@test.com"
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Name, email and password are required"

    
def test_login_wrong_password():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"wrongpass_{uuid.uuid4().hex}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "correct123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "wrong123"
        }
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid email or password"

def test_create_request_without_token():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.post(
        "/requests/",
        json={
            "title": "Laptop repair",
            "description": "Laptop is not turning on"
        }
    )

    assert response.status_code == 401


def test_create_request_with_token():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"request_{uuid.uuid4().hex}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Test Customer",
            "email": email,
            "password": "test123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test123"
        }
    )

    token = login_response.json["access_token"]

    response = client.post(
        "/requests/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Laptop repair",
            "description": "Laptop is not turning on",
            "priority": "MEDIUM"
        }
    )

    assert response.status_code in (200, 201)


def test_customer_cannot_access_admin():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"customer_{uuid.uuid4().hex}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Test Customer",
            "email": email,
            "password": "test123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test123"
        }
    )

    token = login_response.json["access_token"]

    response = client.get(
        "/requests/admin",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_customer_cannot_assign_technician():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"customer_{uuid.uuid4().hex}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Test Customer",
            "email": email,
            "password": "test123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test123"
        }
    )

    token = login_response.json["access_token"]

    response = client.put(
        "/requests/1/assign",
        headers={"Authorization": f"Bearer {token}"},
        json={"technician_id": 2}
    )

    assert response.status_code == 403


def test_customer_cannot_update_request_status():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"customer_{uuid.uuid4().hex}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Test Customer",
            "email": email,
            "password": "test123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "test123"
        }
    )

    token = login_response.json["access_token"]

    response = client.put(
        "/requests/1/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "RESOLVED"}
    )

    assert response.status_code == 403


def test_technician_cannot_update_unassigned_request():
    app = create_app(TestConfig)
    client = app.test_client()

    # Register a customer
    customer_email = f"customer_{uuid.uuid4().hex}@test.com"
    client.post("/auth/register", json={
        "name": "Test Customer",
        "email": customer_email,
        "password": "test123"
    })

    # Register a technician
    technician_email = f"technician_{uuid.uuid4().hex}@test.com"
    client.post("/auth/register", json={
        "name": "Test Technician",
        "email": technician_email,
        "password": "test123"
    })

    # Log in as the technician
    login_response = client.post("/auth/login", json={
        "email": technician_email,
        "password": "test123"
    })
    token = login_response.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to update request ID 1
    response = client.put(
        "/requests/1/status",
        headers=headers,
        json={"status": "IN_PROGRESS"}
    )

    assert response.status_code == 403

def test_customer_cannot_use_invalid_status():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"customer_{uuid.uuid4().hex}@test.com"
    client.post("/auth/register", json={
        "name": "Test Customer",
        "email": email,
        "password": "test123"
    })

    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "test123"
    })

    token = login_response.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(
        "/requests/1/status",
        headers=headers,
        json={"status": "INVALID_STATUS"}
    )

    assert response.status_code == 403
    assert response.json["error"] == "Technician access required"





def test_technician_cannot_set_invalid_status():
    from werkzeug.security import generate_password_hash
    from app.models import User

    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        # Create test users
        customer = User(
            name="Test Customer",
            email=f"customer_{uuid.uuid4().hex}@test.com",
            password=generate_password_hash("test123"),
            role="customer"
        )
        technician = User(
            name="Test Technician",
            email=f"tech_{uuid.uuid4().hex}@test.com",
            password=generate_password_hash("test123"),
            role="technician"
        )
        admin = User(
            name="Test Admin",
            email=f"admin_{uuid.uuid4().hex}@test.com",
            password=generate_password_hash("test123"),
            role="admin"
        )

        db.session.add_all([customer, technician, admin])
        db.session.commit()

        customer_id = customer.id
        technician_id = technician.id
        admin_id = admin.id

    # Log in as customer
    customer_login = client.post("/auth/login", json={
        "email": customer.email,
        "password": "test123"
    })
    customer_headers = {
        "Authorization": f"Bearer {customer_login.json['access_token']}"
    }

    # Create a service request
    create_response = client.post(
        "/requests/",
        headers=customer_headers,
        json={
            "title": "Laptop repair",
            "description": "Laptop not starting",
            "priority": "MEDIUM"
        }
    )
    assert create_response.status_code == 201
    request_id = create_response.json["request_id"]

    # Log in as admin
    admin_login = client.post("/auth/login", json={
        "email": admin.email,
        "password": "test123"
    })
    admin_headers = {
        "Authorization": f"Bearer {admin_login.json['access_token']}"
    }

    # Assign request to technician
    assign_response = client.put(
        f"/requests/{request_id}/assign",
        headers=admin_headers,
        json={"technician_id": technician_id}
    )
    assert assign_response.status_code == 200

    # Log in as technician
    technician_login = client.post("/auth/login", json={
        "email": technician.email,
        "password": "test123"
    })
    technician_headers = {
        "Authorization": f"Bearer {technician_login.json['access_token']}"
    }

    # Attempt an invalid status
    response = client.put(
        f"/requests/{request_id}/status",
        headers=technician_headers,
        json={"status": "INVALID_STATUS"}
    )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid status"



def test_technician_update_nonexistent_request():
    app = create_app(TestConfig)
    client = app.test_client()

    from app import db
    from app.models import User
    from werkzeug.security import generate_password_hash

    # Create a technician
    with app.app_context():
        technician = User(
            name="Test Technician",
            email=f"tech_{uuid.uuid4().hex}@test.com",
            password=generate_password_hash("test123"),
            role="technician"
        )
        db.session.add(technician)
        db.session.commit()
        technician_email = technician.email

    # Log in
    login_response = client.post("/auth/login", json={
        "email": technician_email,
        "password": "test123"
    })
    assert login_response.status_code == 200

    headers = {
        "Authorization": f"Bearer {login_response.json['access_token']}"
    }

    # Use a request ID that should not exist
    response = client.put(
        "/requests/999999/status",
        headers=headers,
        json={"status": "IN_PROGRESS"}
    )

    assert response.status_code == 404
    assert response.json["error"] == "Service request not found"


def test_technician_cannot_update_another_technicians_request():
    from app import db
    from app.models import User, ServiceRequest
    from werkzeug.security import generate_password_hash

    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        password = generate_password_hash("test123")

        technician1 = User(
            name="Technician One",
            email=f"tech1_{uuid.uuid4().hex}@test.com",
            password=password,
            role="technician"
        )
        technician2 = User(
            name="Technician Two",
            email=f"tech2_{uuid.uuid4().hex}@test.com",
            password=password,
            role="technician"
        )
        customer = User(
            name="Test Customer",
            email=f"customer_{uuid.uuid4().hex}@test.com",
            password=password,
            role="customer"
        )

        db.session.add_all([technician1, technician2, customer])
        db.session.commit()

        technician1_email = technician1.email
        technician2_id = technician2.id
        customer_id = customer.id

        service_request = ServiceRequest(
            title="Laptop repair",
            description="Laptop won't start",
            priority="MEDIUM",
            customer_id=customer_id,
            technician_id=technician2_id,
            status="ASSIGNED"
        )
        db.session.add(service_request)
        db.session.commit()
        request_id = service_request.id

    login_response = client.post("/auth/login", json={
        "email": technician1_email,
        "password": "test123"
    })
    assert login_response.status_code == 200

    headers = {
        "Authorization": f"Bearer {login_response.json['access_token']}"
    }

    response = client.put(
        f"/requests/{request_id}/status",
        headers=headers,
        json={"status": "IN_PROGRESS"}
    )

    assert response.status_code == 403
    assert response.json["error"] == "This request is not assigned to you"

def test_technician_update_status_without_json():
    from app import db
    from app.models import User, ServiceRequest
    from werkzeug.security import generate_password_hash

    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        technician = User(
            name="Test Technician",
            email=f"tech_{uuid.uuid4().hex}@test.com",
            password=generate_password_hash("test123"),
            role="technician"
        )
        customer = User(
            name="Test Customer",
            email=f"customer_{uuid.uuid4().hex}@test.com",
            password=generate_password_hash("test123"),
            role="customer"
        )

        db.session.add_all([technician, customer])
        db.session.commit()

        technician_id = technician.id
        technician_email = technician.email
        customer_id = customer.id

        service_request = ServiceRequest(
            title="Laptop repair",
            description="Laptop won't start",
            priority="MEDIUM",
            customer_id=customer_id,
            technician_id=technician_id,
            status="ASSIGNED"
        )

        db.session.add(service_request)
        db.session.commit()
        request_id = service_request.id

    login_response = client.post("/auth/login", json={
        "email": technician_email,
        "password": "test123"
    })
    assert login_response.status_code == 200

    headers = {
        "Authorization": f"Bearer {login_response.json['access_token']}"
    }

    response = client.put(
        f"/requests/{request_id}/status",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json["error"] == "JSON data is required"


def test_technician_update_status_missing_status_field():
    from app import db
    from app.models import User, ServiceRequest
    from werkzeug.security import generate_password_hash

    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        password = generate_password_hash("test123")

        technician = User(
            name="Test Technician",
            email=f"tech_{uuid.uuid4().hex}@test.com",
            password=password,
            role="technician"
        )
        customer = User(
            name="Test Customer",
            email=f"customer_{uuid.uuid4().hex}@test.com",
            password=password,
            role="customer"
        )

        db.session.add_all([technician, customer])
        db.session.commit()

        technician_id = technician.id
        technician_email = technician.email

        service_request = ServiceRequest(
            title="Laptop repair",
            description="Laptop won't start",
            priority="MEDIUM",
            customer_id=customer.id,
            technician_id=technician_id,
            status="ASSIGNED"
        )
        db.session.add(service_request)
        db.session.commit()
        request_id = service_request.id

    login_response = client.post("/auth/login", json={
        "email": technician_email,
        "password": "test123"
    })
    assert login_response.status_code == 200

    headers = {
        "Authorization": f"Bearer {login_response.json['access_token']}"
    }

    response = client.put(
        f"/requests/{request_id}/status",
        headers=headers,
        json={}
    )

    assert response.status_code == 400
    assert response.json["error"] == "JSON data is required"

def test_create_request_missing_title():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"customer_{uuid.uuid4().hex}@test.com"
    client.post("/auth/register", json={
        "name": "Test Customer",
        "email": email,
        "password": "test123"
    })

    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "test123"
    })
    assert login_response.status_code == 200

    headers = {
        "Authorization": f"Bearer {login_response.json['access_token']}"
    }

    response = client.post(
        "/requests/",
        headers=headers,
        json={
            "description": "Laptop won't start",
            "priority": "MEDIUM"
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title and description are required"


def test_create_request_missing_description():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"customer_{uuid.uuid4().hex}@test.com"

    client.post("/auth/register", json={
        "name": "Test Customer",
        "email": email,
        "password": "test123"
    })

    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "test123"
    })
    assert login_response.status_code == 200

    headers = {
        "Authorization": f"Bearer {login_response.json['access_token']}"
    }

    response = client.post(
        "/requests/",
        headers=headers,
        json={
            "title": "Laptop repair",
            "priority": "MEDIUM"
        }
    )

    assert response.status_code == 400
    assert response.json["error"] == "Title and description are required"

 
def test_register_duplicate_email():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"duplicate_{uuid.uuid4().hex}@test.com"

    user_data = {
        "name": "Test Customer",
        "email": email,
        "password": "test123"
    }

    first_response = client.post("/auth/register", json=user_data)
    assert first_response.status_code == 201

    second_response = client.post("/auth/register", json=user_data)

    assert second_response.status_code == 409
    assert second_response.json["error"] == "Email already registered"


def test_register_missing_name():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.post("/auth/register", json={
        "email": f"noname_{uuid.uuid4().hex}@test.com",
        "password": "test123"
    })

    assert response.status_code == 400
    assert response.json["error"] == "Name, email and password are required"


def test_register_missing_email():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.post("/auth/register", json={
        "name": "Test Customer",
        "password": "test123"
    })

    assert response.status_code == 400
    assert response.json["error"] == "Name, email and password are required"



def test_register_duplicate_email():
    app = create_app(TestConfig)
    client = app.test_client()

    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"

    first_response = client.post("/auth/register", json={
        "name": "First Customer",
        "email": email,
        "password": "test123"
    })

    assert first_response.status_code == 201

    second_response = client.post("/auth/register", json={
        "name": "Second Customer",
        "email": email,
        "password": "test456"
    })

    assert second_response.status_code == 409

def test_register_empty_json():
    app = create_app(TestConfig)

    with app.test_client() as client:
        response = client.post("/auth/register", json={})

    assert response.status_code == 400

def test_login_empty_json():
    app = create_app(TestConfig)

    with app.test_client() as client:
        response = client.post("/auth/login", json={})

    assert response.status_code == 400
    
    def test_login_empty_json():
     app = create_app(TestConfig)

    with app.test_client() as client:
        response = client.post("/auth/login", json={})

    assert response.status_code == 400