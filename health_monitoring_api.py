from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HealthMonitoringAPI")

class StructuredMessage:
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return f"{self.message} | {json.dumps(self.kwargs)}"
    
# Mock in-memory databases 
users = {}
devices = {}
appointments = []
messages = []

# Generate sequential IDs
def generate_id(entity_dict):
    """Generates a sequential integer ID."""
    if entity_dict:
        return max(entity_dict.keys()) + 1
    else:
        return 1

def add_or_update_entity(entity_dict, entity_id, data):
    """Adds or updates an entity in the given dictionary."""
    entity_dict[entity_id] = data
    
@app.route('/')
def index():
    """Root URL response."""
    return 'Health Monitoring API is running!'

@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.json
    if not all(k in data for k in ['name', 'email']):
        return jsonify({"error": "Missing name or email"}), 400
    user_id = generate_id(users)
    add_or_update_entity(users, user_id, {"name": data['name'], "email": data['email'], "roles": []})
    return jsonify({"userId": user_id, "status": "success"})

@app.route('/users/<int:user_id>/assignRole', methods=['POST'])
def assign_role(user_id):
    data = request.json
    if 'roles' not in data:
        return jsonify({"error": "Missing roles"}), 400
    if user_id in users:
        users[user_id]['roles'] = data['roles']
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/devices/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = generate_id(devices)
    add_or_update_entity(devices, device_id, {"deviceId": data['deviceId'], "type": data['type'], "status": "enabled"})
    return jsonify({"status": "success"})

@app.route('/patients/<int:patient_id>/measurements', methods=['POST'])
def submit_measurement(patient_id):
    data = request.json
    measurement_type = data['type']
    value = data.get('value')
    if value is None or not isinstance(value, (int, float)):
        return jsonify({"error": "Invalid measurement value"}), 400

    thresholds = {
        'bloodPressure': {'low': 90, 'high': 140},
        'temperature': {'low': 36.5, 'high': 37.5},
        'glucoseLevel': {'low': 70, 'high': 140},
    }

    if measurement_type in thresholds:
        threshold = thresholds[measurement_type]
        if not threshold['low'] <= value <= threshold['high']:
            generate_alert(patient_id, measurement_type, value, threshold)
            return jsonify({"status": "success", "alert": "Measurement outside of threshold"})
    else:
        return jsonify({"status": "success", "alert": "No threshold set for this measurement type"})

def generate_alert(patient_id, measurement_type, value, threshold):
    logger.info(StructuredMessage("ALERT",
                                   patient_id=patient_id,
                                   measurement_type=measurement_type,
                                   value=value,
                                   threshold=threshold))

@app.route('/patients/<int:patient_id>/appointments/book', methods=['POST'])
def book_appointment(patient_id):
    data = request.json
    appointment_id = len(appointments) + 1
    appointments.append({"appointmentId": appointment_id, "patientId": patient_id, "mpId": data['mpId'], "time": data['time']})
    return jsonify({"appointmentId": appointment_id, "status": "success"})

@app.route('/patients/<int:patient_id>/appointments', methods=['GET'])
def view_appointments(patient_id):
    patient_appointments = [appointment for appointment in appointments if appointment['patientId'] == patient_id]
    return jsonify(patient_appointments)

@app.route('/chat/<int:patient_id>', methods=['POST'])
def post_message(patient_id):
    data = request.json
    message = {"patientId": patient_id, "content": data['content'], "timestamp": datetime.now(timezone.utc).isoformat()}
    messages.append(message)
    return jsonify({"status": "success"})

@app.route('/chat/<int:patient_id>', methods=['GET'])
def get_chat_history(patient_id):
    chat_history = [message for message in messages if message['patientId'] == patient_id]
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)

