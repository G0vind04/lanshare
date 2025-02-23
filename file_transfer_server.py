import socket
import struct
from tqdm import tqdm

def start_server(port, status_callback=None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    
    message = f"Server is running and waiting for incoming files on port {port}..."
    if status_callback:
        status_callback(message)
    print(message)  # Keep console output for debugging

    while True:
        client_socket, addr = server_socket.accept()
        message = f"\n[RECEIVING] Connection from {addr}"
        if status_callback:
            status_callback(message)
        print(message)

        try:
            # Receive the file name length (first 4 bytes)
            file_name_length = struct.unpack("I", client_socket.recv(4))[0]

            # Receive the file name
            file_name = client_socket.recv(file_name_length).decode('utf-8')
            message = f"[RECEIVING] File name: {file_name}"
            if status_callback:
                status_callback(message)
            print(message)

            # Get the file size (optional, but useful for progress bar)
            file_size = 0
            with open(file_name, 'wb') as f:
                with tqdm(unit='B', unit_scale=True, desc="Receiving") as pbar:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        f.write(data)
                        pbar.update(len(data))  # Update the progress bar
                        file_size += len(data)
                        
                        # Update GUI progress every 1MB
                        if file_size % (1024 * 1024) == 0 and status_callback:
                            status_callback(f"[PROGRESS] Received: {file_size/1024/1024:.1f} MB")

            message = f"[RECEIVED] File '{file_name}' ({file_size} bytes) has been successfully received."
            if status_callback:
                status_callback(message)
            print(message)

        except Exception as e:
            error_message = f"[ERROR] An error occurred while receiving file: {str(e)}"
            if status_callback:
                status_callback(error_message)
            print(error_message)
        
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server(12345)  # When run directly, start without GUI callback