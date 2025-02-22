import socket
import struct

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    print(f"Server is running and waiting for incoming files on port {port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"\n[RECEIVING] Connection from {addr}")

        # Receive the file name length (first 4 bytes)
        file_name_length = struct.unpack("I", client_socket.recv(4))[0]

        # Receive the file name
        file_name = client_socket.recv(file_name_length).decode('utf-8')
        print(f"[RECEIVING] File name: {file_name}")

        # Receive the file data
        with open(file_name, 'wb') as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)

        print(f"[RECEIVED] File '{file_name}' has been successfully received.")
        client_socket.close()