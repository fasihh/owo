import socket
import os
import threading
from dotenv import load_dotenv

load_dotenv()

HOST_NAME = os.getenv('HOST_NAME') or 'localhost'
PORT = int(os.getenv('PORT') or '3001')
BUFFER_SIZE = int(os.getenv('BUFFER_SIZE') or '1024')
HEADER_SIZE = int(os.getenv('HEADER_SIZE') or '256')

PAYLOAD_SIZE = BUFFER_SIZE - HEADER_SIZE

def receive_message(client_socket: socket.SocketType) -> None:
  while True:
    try:
      message = client_socket.recv(BUFFER_SIZE).decode('utf-8')
      if not message:
        break
      message_header = message[:HEADER_SIZE].strip()
      message_content = message[HEADER_SIZE:].strip()

      print(f"\r{message_header}: {message_content}\n>> ", end="")
    except Exception as e:
      print(f'Connection Error: {e}')
      client_socket.close()
      break

def start_client() -> None:
  client_name = input('name: ').strip()[:HEADER_SIZE]
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((HOST_NAME, PORT))
  print(f'Connected to server: {HOST_NAME}:{PORT}')

  thread = threading.Thread(target=receive_message, args=(client_socket,))
  thread.daemon = True
  thread.start()

  try:
    while True:
      message = input('>> ').strip()[:PAYLOAD_SIZE]
      if message.lower() == 'quit':
        break
      client_socket.send(f'{client_name:<{HEADER_SIZE}}{message:<{PAYLOAD_SIZE}}'.encode('utf-8'))
  except KeyboardInterrupt:
    print('Closing...')
  except Exception as e:
    print(f'Error: {e}')
  
  client_socket.close()
  
if __name__ == '__main__':
  start_client()