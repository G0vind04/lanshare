import socket
import os
import struct

def send_file(ip, port, file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    print(f"[SENDING] Connected to {ip}:{port}. Sending file...")

    # Send the file name length (4 bytes)
    file_name = os.path.basename(file_path)
    file_name_length = len(file_name.encode('utf-8'))
    client_socket.send(struct.pack("I", file_name_length))

    # Send the file name
    client_socket.send(file_name.encode('utf-8'))

    # Send the file data
    with open(file_path, 'rb') as f:
        while True:
            bytes_read = f.read(1024)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)

    print(f"[SENT] File '{file_name}' has been successfully sent.")
    client_socket.close()

if __name__ == "__main__":
    send_file('192.168.1.10', 12345, 'path_to_your_file')