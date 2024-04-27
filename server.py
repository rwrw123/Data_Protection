import socket
import threading
import json
import queue
import re

# This queue will hold tuples of (connection object, address, message)
inquiry_queue = queue.Queue()

#Remove strip excess whitespace and potential harmful characters
def sanitize_input(input_str):
    return re.sub(r'[<>{}]', '',input_str.strip())

def handle_client(conn, addr, inquiry_queue):
    """Handles incoming client connections."""
    print(f"Connected by {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            message = json.loads(data.decode('utf-8'))
            sanitized_message = {key: sanitize_input(value) if isinstance(value, str) else value for key, value in message.items()}
            # Print santized messages conditionally, skip printing for inquiries
            if sanitized_message['type'] != 'inquiry':
                print(f"Received message from {addr}: {sanitized_message['content']}")

            if sanitized_message['type'] == 'inquiry':
                # Handle inquiries by adding them to the queue
                inquiry_queue.put((conn, addr, sanitized_message))
        except Exception as e:
            print(f"Error handling message from {addr}: {e}")
            break
    conn.close()

def start_server(host, port, inquiry_queue):
    """Starts the server and listens for incoming connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, inquiry_queue))
            client_thread.start()

def response_handler(inquiry_queue):
    """Processes inquiries from the queue and prompts for responses."""
    while True:
        conn, addr, inquiry = inquiry_queue.get()
        print(f"\nReceived inquiry from {addr}: {inquiry['content']}")
        response_content = input("Type your response: ")
        response = {"type": "response", "content": response_content}
        try:
            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            print(f"Error sending response to {addr}: {e}")
        inquiry_queue.task_done()

if __name__ == "__main__":
    host = 'localhost'
    port = 65432  

    # Start the server
    server_thread = threading.Thread(target=start_server, args=(host, port, inquiry_queue))
    server_thread.start()

    # Start the response handler thread
    response_thread = threading.Thread(target=response_handler, args=(inquiry_queue,), daemon=True)
    response_thread.start()

    print("Server is running. Responses to inquiries can be typed in the console.")




