import socket
import struct
from tqdm import tqdm
import tkinter as tk
from tkinter import messagebox

def start_server(port, status_callback=None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    
    message = f"Server is running and waiting for incoming transfers on port {port}..."
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
            # Receive transfer type (1 for file, 2 for text)
            transfer_type = struct.unpack("I", client_socket.recv(4))[0]
            
            if transfer_type == 1:  # File transfer
                # Receive the file name length
                file_name_length = struct.unpack("I", client_socket.recv(4))[0]
                
                # Receive the file name
                file_name = client_socket.recv(file_name_length).decode('utf-8')
                message = f"[RECEIVING] File name: {file_name}"
                if status_callback:
                    status_callback(message)
                print(message)
                
                # Get the file size (optional, but useful for progress bar)
                file_size = 0
                with open(f"received_{file_name}", 'wb') as f:
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
                
            elif transfer_type == 2:  # Text transfer
                # Receive text size
                text_size = struct.unpack("I", client_socket.recv(4))[0]
                
                message = f"[RECEIVING] Text message of size: {text_size} bytes"
                if status_callback:
                    status_callback(message)
                print(message)
                
                # Receive text data
                received_data = bytearray()
                with tqdm(total=text_size, unit='B', unit_scale=True, desc="Receiving") as pbar:
                    while len(received_data) < text_size:
                        chunk = client_socket.recv(min(1024, text_size - len(received_data)))
                        if not chunk:
                            break
                        received_data.extend(chunk)
                        pbar.update(len(chunk))
                
                # Convert received bytes to text
                received_text = received_data.decode('utf-8')
                
                # Update the status with the actual received text
                message = f"[RECEIVED] Text message: {received_text}"
                if status_callback:
                    status_callback(message)
                print(message)
                
                # Show received text in a popup
                def show_popup():
                    root = tk.Tk()
                    root.withdraw()  # Hide the main window
                    messagebox.showinfo("Text Received", received_text)
                    root.destroy()
                
                # Show popup in the main thread
                if status_callback:
                    root = tk.Tk()
                    root.after(100, lambda: messagebox.showinfo("Text Received", received_text))
                    root.withdraw()  # Hide the main window to only show the popup
                
        except Exception as e:
            error_message = f"[ERROR] An error occurred while receiving: {str(e)}"
            if status_callback:
                status_callback(error_message)
            print(error_message)
        
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server(12345)  # When run directly, start without GUI callback