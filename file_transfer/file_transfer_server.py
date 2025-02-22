import socket

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    print(f"Server is running and waiting for incoming files on port {port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"\n[RECEIVING] Connection from {addr}")
        with open('received_file', 'wb') as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
        print("[RECEIVED] File has been successfully received.")
        client_socket.close()

if __name__ == "__main__":
    start_server(12345)