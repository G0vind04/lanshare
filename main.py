from peer_discovery import PeerDiscovery
from file_transfer_server import start_server
from hotkey_trigger import trigger_file_transfer
import threading

def main():
    # Start peer discovery
    peer_discovery = PeerDiscovery()
    peer_discovery.register_service("MyDevice", 12345)
    peer_discovery.discover_peers()

    # Start file transfer server in a separate thread
    server_thread = threading.Thread(target=start_server, args=(12345,))
    server_thread.daemon = True
    server_thread.start()

    # Start hotkey trigger
    trigger_file_transfer(peer_discovery.peers)

if __name__ == "__main__":
    main()