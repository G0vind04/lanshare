import socket
import os
import struct
from tqdm import tqdm  # For progress bar

def send_file(ip, port, data):
    """
    Send either a file or text data to a specified host and port
    
    Args:
        ip (str): The host IP address to send to
        port (int): The port number to connect to
        data (str): Either a file path or text content to send
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    
    try:
        # Check if data is a file path or text content
        is_file = os.path.isfile(data)
        
        if is_file:
            # Send indicator for file transfer (1)
            client_socket.send(struct.pack("I", 1))
            
            # Get the file size and name
            file_name = os.path.basename(data)
            file_size = os.path.getsize(data)
            
            # Send the file name length (4 bytes)
            file_name_length = len(file_name.encode('utf-8'))
            client_socket.send(struct.pack("I", file_name_length))
            
            # Send the file name
            client_socket.send(file_name.encode('utf-8'))
            
            # Send the file data with a progress bar
            print(f"[SENDING] Connected to {ip}:{port}. Sending file...")
            with open(data, 'rb') as f:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc="Sending") as pbar:
                    while True:
                        bytes_read = f.read(1024)
                        if not bytes_read:
                            break
                        client_socket.sendall(bytes_read)
                        pbar.update(len(bytes_read))
            
            print(f"[SENT] File '{file_name}' has been successfully sent.")
            
        else:
            # Send indicator for text transfer (2)
            client_socket.send(struct.pack("I", 2))
            
            # Convert text to bytes
            text_bytes = data.encode('utf-8')
            text_size = len(text_bytes)
            
            # Send text size
            client_socket.send(struct.pack("I", text_size))
            
            # Send text data with progress bar
            print(f"[SENDING] Connected to {ip}:{port}. Sending text...")
            with tqdm(total=text_size, unit='B', unit_scale=True, desc="Sending") as pbar:
                start = 0
                chunk_size = 1024
                while start < text_size:
                    end = min(start + chunk_size, text_size)
                    chunk = text_bytes[start:end]
                    client_socket.sendall(chunk)
                    pbar.update(len(chunk))
                    start = end
            
            print("[SENT] Text has been successfully sent.")
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    send_file('192.168.1.10', 12345, 'path_to_your_file')