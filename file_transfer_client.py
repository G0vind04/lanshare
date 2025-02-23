import socket
import os
import struct
from tqdm import tqdm  # For progress bar

def send_file(ip, port, file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    print(f"[SENDING] Connected to {ip}:{port}. Sending file...")

    # Get the file size
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Send the file name length (4 bytes)
    file_name_length = len(file_name.encode('utf-8'))
    client_socket.send(struct.pack("I", file_name_length))

    # Send the file name
    client_socket.send(file_name.encode('utf-8'))

    # Send the file data with a progress bar
    with open(file_path, 'rb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Sending") as pbar:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
                pbar.update(len(bytes_read))  # Update the progress bar

    print(f"[SENT] File '{file_name}' has been successfully sent.")
    client_socket.close()

if __name__ == "__main__":
    send_file('192.168.1.10', 12345, 'path_to_your_file')