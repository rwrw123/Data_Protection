import bcrypt
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime, timezone
import logging
import re
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/health_db"
mongo = PyMongo(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HealthMonitoringAPI")

@app.route('/')
def index():
    """Root URL response."""
    return 'Health Monitoring API is running!'

@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # Validate email, name, and password
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(name) < 2 or len(name) > 50:
        return jsonify({"error": "Name must be between 2 and 50 characters long"}), 400
    if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
        return jsonify({"error": "Password must be at least 8 characters long and include letters and numbers"}), 400

    # Securely store user data
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_id = mongo.db.users.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.now(timezone.utc)
    }).inserted_id
    return jsonify({"userId": str(user_id), "status": "success"})

@app.route('/users/<user_id>/assignRole', methods=['POST'])
def assign_role(user_id):
    data = request.json
    roles = data.get('roles', [])

    # Validate roles
    valid_roles = ["admin", "user", "viewer"]  
    if any(role not in valid_roles for role in roles):
        return jsonify({"error": "Invalid role specified"}), 400

    # Update roles securely
    result = mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"roles": roles}}
    )
    if result.matched_count:
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/devices/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('deviceId', '').strip()
    device_type = data.get('type', '').strip()

    # Validate device_id and device_type
    if not re.match(r"^[a-zA-Z0-9]{10,20}$", device_id):
        return jsonify({"error": "Invalid device ID format"}), 400
    if device_type not in ["type1", "type2", "type3"]: 
        return jsonify({"error": "Invalid device type"}), 400

    # Securely store device data
    result = mongo.db.devices.insert_one({
        "deviceId": device_id,
        "type": device_type,
        "registration_date": datetime.now(timezone.utc)
    })
    return jsonify({"deviceId": str(result.inserted_id), "status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
