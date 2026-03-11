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
  - nm/system_info_resp
- GUI responses:
  - gui/rx/nm/scan_wifi_resp
  - gui/rx/nm/list_wifi_resp
  - gui/rx/nm/wired_info_resp
  - gui/rx/nm/wireless_info_resp
  - gui/rx/nm/system_info_resp

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

5. system_info
- Command:
  - nm/system_info (legacy)
  - gui/tx/nm/system_info (GUI)
- Payload:
  - Ignored — publish with empty payload or any value (e.g. `{}` or `{"command": "get_info"}`).
- Response:
  - nm/system_info_resp (legacy)
  - gui/rx/nm/system_info_resp (GUI)
- Functionality:
  - Retrieves static system information about the host machine.
  - Publishes a single JSON object to the response topic.
- Response JSON fields:
  - `Device Name` — Pretty hostname from /etc/machine-info, falls back to system hostname.
  - `Hostname` — System hostname.
  - `Operating System` — OS description from lsb_release, falls back to platform string.
  - `Kernel` — Kernel name and release (e.g. "Linux 5.15.0-91-generic").
  - `Architecture` — CPU architecture (e.g. "x86_64").
  - `Processor` — CPU model string from /proc/cpuinfo.
  - `Memory` — Total RAM as human-readable string (e.g. "16.0 GB").
  - `Graphics` — First VGA/3D controller from lspci; "Unknown" if lspci unavailable.
  - `Disk Space` — Total root filesystem size as human-readable string (e.g. "512 GB").
- Example response:
  ```json
  {
    "Device Name": "Linux Box",
    "Hostname": "cargt-device-01",
    "Operating System": "Ubuntu 22.04.3 LTS",
    "Kernel": "Linux 5.15.0-91-generic",
    "Architecture": "x86_64",
    "Processor": "Intel Core i7-10700K @ 3.80GHz",
    "Memory": "16.0 GB",
    "Graphics": "Intel UHD Graphics 630",
    "Disk Space": "512 GB"
  }
  ```

Summary
- The backend listens for both legacy and GUI-prefixed commands.
- It responds on the appropriate topic, matching the prefix of the request (legacy or GUI).
- All topic prefixes are configurable via class variables for flexibility.
- The code is structured to allow easy extension for new commands and topics.
