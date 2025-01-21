import socket
import os
import threading
from typing import List
from dotenv import load_dotenv

load_dotenv()

HOST_NAME = os.getenv('HOST_NAME') or 'localhost'
PORT = int(os.getenv('PORT') or '3001')
BUFFER_SIZE = 1024
HEADER_SIZE = 256

PAYLOAD_SIZE = BUFFER_SIZE - HEADER_SIZE

clients: List[socket.SocketType] = []

def broadcast(message: str, sender_socket: socket.SocketType) -> None:
  for client in clients:
    if sender_socket == client:
      continue
    try:
      client.send(message.encode('utf-8'))
    except Exception as e:
      print(f'Error sending message: {e}')
      client.close()
      clients.remove(client)

def handle_client(client_socket: socket.SocketType, client_address) -> None:
  print(f'{client_address} connected')
  client_socket.send(f'{'Server':<{HEADER_SIZE}}{'Welcome from server!':<{PAYLOAD_SIZE}}'.encode('utf-8'))
  while True:
    try:
      message = client_socket.recv(BUFFER_SIZE).decode('utf-8')
      if not message:
        break
      message_header = message[:HEADER_SIZE].strip()
      message_content = message[HEADER_SIZE:].strip()
      print(f'{client_address} | {message_header}: {message_content}')
      broadcast(message, client_socket)
    except Exception as e:
      print(f'Error with client {client_address}: {e}')
      break

  clients.remove(client_socket)
  client_socket.close()
  print(f'{client_address} removed')

def start_server() -> None:
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.bind((HOST_NAME, PORT))
  server_socket.listen(5)
  print(f'Server listening at: {HOST_NAME}:{PORT}')

  try:
    while True:
      client_socket, client_address = server_socket.accept()
      clients.append(client_socket)

      thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
      thread.daemon = True
      thread.start()
  except KeyboardInterrupt:
    print('Closing server')
  finally:
    for client in clients:
      client.close()
    server_socket.close()

if __name__ == '__main__':
  start_server()
