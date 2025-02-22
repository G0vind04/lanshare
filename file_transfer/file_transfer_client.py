import socket

def send_file(ip, port, file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    print(f"[SENDING] Connected to {ip}:{port}. Sending file...")

    with open(file_path, 'rb') as f:
        while True:
            bytes_read = f.read(1024)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)

    print("[SENT] File has been successfully sent.")
    client_socket.close()

if __name__ == "__main__":
    send_file('192.168.1.10', 12345, 'path_to_your_file')