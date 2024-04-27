import socket
import threading
import json

def send_message(s, message):
    try:
        s.sendall(json.dumps(message).encode('utf-8'))
    except Exception as e:
        print(f"Failed to send message: {e}")

def receive_message(s, stop_event):
    while not stop_event.is_set():
        try:
            data = s.recv(1024)
            if not data:
                break
            message = json.loads(data.decode('utf-8'))
            print(f"\nReceived: {message['content']}\n> ", end='', flush=True)
        except Exception as e:
            if stop_event.is_set():
                break
            print(f"\nError receiving message: {e}\n> ", end='', flush=True)

def main():
    host, port = 'localhost', 65432
    stop_event = threading.Event()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            print(f"Connection to {host}:{port} failed.")
            return

        threading.Thread(target=receive_message, args=(s, stop_event), daemon=True).start()

        while not stop_event.is_set():
            print("\nOptions:")
            print("1. Send 'How are you doing?' inquiry")
            print("2. Send a custom message")
            print("3. Exit")
            choice = input("> ")

            if choice == '1':
                msg = {'type': 'inquiry', 'content': 'How are you doing?'}
                send_message(s, msg)
            elif choice == '2':
                custom_message = input("Enter your message: ")
                msg = {'type': 'message', 'content': custom_message}
                send_message(s, msg)
            elif choice == '3':
                print("Exiting...")
                stop_event.set()

if __name__ == "__main__":
    main()











