MQTT Topics and Functionality Documentation

Topic Prefixes
- Legacy/Backend Prefix:
  - nm/ — Used for all standard backend MQTT topics.
- GUI Prefixes:
  - gui/tx/nm/ — Topics the GUI publishes to (commands sent to backend).
  - gui/rx/nm/ — Topics the backend publishes to for GUI responses.

Subscribed Topics
- nm/# — The backend subscribes to all legacy topics for direct backend control.
- gui/tx/nm/# — The backend subscribes to all GUI-originated commands.

Published Topics
- Backend responses (legacy):
  - nm/scan_wifi_resp
  - nm/list_wifi_resp
  - nm/wired_info_resp
  - nm/wireless_info_resp
- GUI responses:
  - gui/rx/nm/scan_wifi_resp
  - gui/rx/nm/list_wifi_resp
  - gui/rx/nm/wired_info_resp
  - gui/rx/nm/wireless_info_resp

Command Topics and Functionality

1. scan_wifi
- Command:
  - nm/scan_wifi (legacy)
  - gui/tx/nm/scan_wifi (GUI)
- Response:
  - nm/scan_wifi_resp (legacy)
  - gui/rx/nm/scan_wifi_resp (GUI)
- Functionality:
  - Initiates a WiFi scan on the specified interface (or default if none).
  - Responds with scan status and summary.
  - Publishes details of each found network to the corresponding response topic.

2. list_wifi
- Command:
  - nm/list_wifi (legacy)
  - gui/tx/nm/list_wifi (GUI)
- Response:
  - nm/list_wifi_resp (legacy)
  - gui/rx/nm/list_wifi_resp (GUI)
- Functionality:
  - Lists available WiFi networks on the specified interface.
  - Publishes each network's details to the response topic.

3. wired_info
- Command:
  - nm/wired_info (legacy)
  - gui/tx/nm/wired_info (GUI)
- Response:
  - nm/wired_info_resp (legacy)
  - gui/rx/nm/wired_info_resp (GUI)
- Functionality:
  - Retrieves information about the wired network interface.
  - Publishes the info as a JSON object to the response topic.

4. wireless_info
- Command:
  - nm/wireless_info (legacy)
  - gui/tx/nm/wireless_info (GUI)
- Response:
  - nm/wireless_info_resp (legacy)
  - gui/rx/nm/wireless_info_resp (GUI)
- Functionality:
  - Retrieves information about the wireless network interface.
  - Publishes the info as a JSON object to the response topic.

Summary
- The backend listens for both legacy and GUI-prefixed commands.
- It responds on the appropriate topic, matching the prefix of the request (legacy or GUI).
- All topic prefixes are configurable via class variables for flexibility.
- The code is structured to allow easy extension for new commands and topics.
