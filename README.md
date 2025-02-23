# LANSHARE - P2P File Transfer

## Overview
LANSHARE P2P File Transfer is a simple, lightweight peer-to-peer file sharing application with a retro-themed GUI. It allows users to:
- Discover peers on the same local network
- Drag and drop files to send to selected peers
- Receive files seamlessly in the background

## Features
- **Peer Discovery**: Uses Zeroconf to find other users on the same network.
- **Drag-and-Drop Support**: Quickly select files for transfer.
- **File Reception**: Runs a background server to receive incoming files.
- **Retro-Themed UI**: Classic interface with green text and a nostalgic feel.

## Installation
### Prerequisites
Ensure you have Python installed. Then, install the required dependencies:
```bash
pip install zeroconf
```

## Running the Application
To start the application, run:
```bash
python gui_app.py
```

## How to Use
1. Launch the application.
2. Wait for peers to appear in the discovered peers list.
3. Drag and drop a file onto the interface or use the "Select File" button.
4. Select a peer from the list and click "Send File."
5. The file will be transferred instantly.

## Future Enhancements
- Progress indicators for file transfers.
- End-to-end encryption for security.
- Cross-platform support for macOS and Linux.

## License
This project is open-source and available under the MIT License.

## Contributors
Developed by  <a href="https://github.com/kidobop" target="_blank">Aaqil Fazil </a>and <a href="https://github.com/g0vind04" target="_blank">Govind Mohan</a> . Feel free to contribute and improve the project!

