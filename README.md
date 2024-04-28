# Data_Protection

## Health Monitoring API

### Changes in health_monitoring_api.py
- Device Resgistration
  - Endpoint: POST /devices/register
  - Validation:
    - deviceId must be an alphanumeric string between 10 to 20 characters
    - type must be one of the predefined device types (e.g., type1, type2, type3).
  - Purpose:
      Ensures that all registered devices have valid identifiers and types, preventing errors and malicious data entries.
- Measurement Submission
  - Endpoint: POST /patients/<int:patient_id>/measurements/add
  - Validation:
    - measurement_type must be one of the accepted types (e.g., temperature, blood_pressure, heart_rate)
    - value must be a numeric data type (integer or float)
  - Purpose:
      Validates measurement types and values to maintain data quality and accuracy.
- Appointment Booking
  - Endpoint: POST /patients/<int:patient_id>/appointments/book
  - Validation:
    - mp_id (medical personnel ID) must be a numeric string exactly 5 digits long
    - time must follow the ISO 8601 date-time format
    - Purpose:
        Ensures that appointments are scheduled with correct and valid data, enhancing the reliability of the scheduling system.
### Changes in app.py
- User Registration
  - Endpoint: POST /users/add
  - Enhancements:
    - Email, name, and password fields are validated for format and content.
    - Passwords are securely hashed using bcrypt before storage to ensure data security.
    - Provides detailed error messages for invalid inputs to assist in troubleshooting and user guidance.
- Role Assignment
  - Endpoint: POST /users/<user_id>/assignRole
  - Enhancements:
    - Role updates are checked against a list of valid roles to prevent unauthorized role assignments.
    - Secure updates to user roles using MongoDB transactions to ensure database integrity.
- Device Registration
  - Endpoint: POST /devices/register
  - Enhancements:
      - Device IDs and types are strictly validated using regular expressions and predefined lists to ensure they meet system requirements.
      - Securely stores device information with validation feedback on incorrect inputs.

## P2P Project
