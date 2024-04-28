from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime, timezone
import logging
import json
import re
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/health_db"
mongo = PyMongo(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HealthMonitoringAPI")

class StructuredMessage:
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return f"{self.message} | {json.dumps(self.kwargs)}"
    
@app.route('/')
def index():
    """Root URL response."""
    return 'Health Monitoring API is running!'

@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.json
    # validates name and email
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": "Invalid email format"}), 400
    #check name length
    if len(name) <3 or len(name)>50:
        return jsonify({"error":"Name must be between 3 to 50 characters long"}), 400
    result = mongo.db.users.insert_one({
        "name": data['name'],
        "email": data['email'],
        "roles": data.get('roles',[])
    })
    return jsonify({"userId": str(result.inserted_id), "status": "success"})

@app.route('/users/<user_id>/assignRole', methods=['POST'])
def assign_role(user_id):
    data = request.json
    roles = data.get('roles',[])
    #validates roles
    valid_roles = ["admin", "user","viewer"]
    if any(role not in valid_roles for role in roles):
        return jsonify({"error":"Invalid role specified"}), 400
    #updates validated roles
    result = mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set":{"roles": roles}}
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
    
    #new validations
    if not re.match(r"^[a-zA-Z0-9]{10,20}$", device_id):
        return jsonify({"error": "Invalid device ID format"}), 400
    if device_type not in ["type1", "type2", "type3"]:  # Example types
        return jsonify({"error": "Invalid device type"}), 400

    result = mongo.db.devices.insert_one({
        "deviceId": device_id,
        "type": device_type,
        "registration_data": datetime.now(timezone.utc)
    })
    return jsonify({"deviceId":str(result.inserted_id), "status": "success"})

@app.route('/patients/<int:patient_id>/measurements/add', methods=['POST'])
def submit_measurement(patient_id):
    data = request.json
    measurement_type = data.get('type', '').strip()
    value = data.get('value',0)
    
    #(new)Validation for measurement type and val
    if measurement_type not in ["temperature","blood_pressure","heart_rate"]:
        return jsonify({"error": "Invalid measurement type"}), 400
    if not isinstance(value, (int,float)):
        return jsonify({"error": " Invalid measurement value"}), 400
    
    mongo.db.measurements.insert_one({
        "patient_id": patient_id,
        "type": measurement_type,
        "value" : value,
        "timestamp": datetime.now(timezone.utc)
    })
    return jsonify({"status": "success"})

@app.route('/patients/<int:patient_id>/appointments/book', methods=['POST'])
def book_appointment(patient_id):
    data = request.json
    mp_id =data.get('mpId', '').strip()
    time = data.get('time', '')

# Validate mp_id and time
    if not re.match(r"^[0-9]{5}$", mp_id):
        return jsonify({"error": "Invalid medical personnel ID"}), 400
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", time):  # ISO 8601 format
        return jsonify({"error": "Invalid time format"}), 400
    
    result = mongo.db.appointments.insert_one({
        "patient_id": patient_id,
        "mp_id": mp_id,
        "time": time
    })
    return jsonify({"appointmentId": str(result.inserted_id), "status": "success"})

@app.route('/patients/<int:patient_id>/appointments', methods=['GET'])
def view_appointments(patient_id):
    patient_appointments = list(mongo.db.appointments.find({"patient_id": patient_id}))
    return jsonify(patient_appointments)

@app.route('/chat/<int:patient_id>', methods=['POST'])
def post_message(patient_id):
    data = request.json
    message = {
        "patient_id": patient_id,
        "content": data['content'],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    mongo.db.messages.insert_one(message)
    return jsonify({"status": "success"})

@app.route('/chat/<int:patient_id>', methods=['GET'])
def get_chat_history(patient_id):
    chat_history = list(mongo.db.messages.find({"patient_id": patient_id}))
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)
