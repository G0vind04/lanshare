from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
import socket

class PeerDiscovery:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.peers = {}

    def register_service(self, name, port):
        info = ServiceInfo(
            "_filetransfer._tcp.local.",
            f"{name}._filetransfer._tcp.local.",
            addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
            port=port,
            properties={},
        )
        self.zeroconf.register_service(info)

    def discover_peers(self):
        class MyListener:
            def __init__(self, peers):
                self.peers = peers

            def add_service(self, zeroconf, type, name):
                info = zeroconf.get_service_info(type, name)
                if info:
                    self.peers[name] = {
                        "address": socket.inet_ntoa(info.addresses[0]),
                        "port": info.port,
                    }
                    print(f"Discovered peer: {name} at {self.peers[name]['address']}:{self.peers[name]['port']}")

        listener = MyListener(self.peers)
        browser = ServiceBrowser(self.zeroconf, "_filetransfer._tcp.local.", listener)

    def close(self):
        self.zeroconf.close()