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
### Changes in client.py
- Function: sanitize_input(input_str)
- Purpose:
    - This function sanitizes user input by removing potentially harmful characters that could be used in injection attacks.
- Methodology:
    - It uses a regular expression to filter out any occurrences of <, >, {, or }.
    - These characters are often used in scripting and markup languages to denote special syntax, so stripping them from input can prevent certain types of injection attacks, such as HTML or JavaScript injection.
- Usage in Client Script:
    - Applied to each piece of user input that forms part of the message data structure before it is serialized into JSON and sent over the network.
    - Ensures that the data sent from the client to the server is devoid of characters that could be used maliciously.
- Usage
  <img width="948" alt="Screen Shot 2024-04-28 at 9 11 20 PM" src="https://github.com/rwrw123/Data_Protection/assets/113308286/8e39bc19-9c7f-487f-b288-1359ef90d9d9">

### Changes in server.py
- Application:
    - The server uses the sanitization function on all incoming data before processing it.
    - This is a defensive programming practice to ensure that even if the client fails to properly sanitize data, the server provides an additional layer of security.
- Process Flow:
  - Data received over the network is first decoded and deserialized from JSON.
  - Each message, particularly its content, is sanitized using the sanitize_input function.
  - The sanitized content is then used in further server-side processing or stored, reducing the risk of harmful data being executed or stored.
- Usage
  <img width="995" alt="Screen Shot 2024-04-28 at 9 12 38 PM" src="https://github.com/rwrw123/Data_Protection/assets/113308286/097692e7-c669-49b8-9ffb-e897db3a513e">


