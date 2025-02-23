import keyboard
from file_transfer_client import send_file

def trigger_file_transfer(peers):
    print("\nPress Ctrl+Shift+F to initiate file transfer.")
    keyboard.wait('ctrl+shift+f')
    print("\nFile transfer initiated!")

    # Prompt the user to choose between sending or receiving
    action = input("Do you want to [S]end or [R]eceive a file? (S/R): ").strip().upper()

    if action == 'S':
        # Sending a file
        print("[SEND MODE] Please provide the peer's IP address and file path.")
        ip = input("Enter peer's IP address: ")
        file_path = input("Enter file path: ")
        send_file(ip, 12345, file_path)

    elif action == 'R':
        # Receiving a file (server is already running in the background)
        print("[RECEIVE MODE] Waiting for incoming files...")

    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    trigger_file_transfer({})