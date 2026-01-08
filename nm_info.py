import sdbus
import time
import asyncio
import uuid
import asyncio

from sdbus_async.networkmanager import (
    NetworkManager,
    NetworkDeviceGeneric,
    NetworkDeviceWireless,
    NetworkDeviceWired,
    NetworkConnectionSettings,
    IPv4Config,
    AccessPoint,
    NetworkManagerSettings,
)

from sdbus_async.networkmanager.settings import (ConnectionProfile)
from sdbus_async.networkmanager.settings import (ConnectionSettings)

from sdbus_async.networkmanager.enums import DeviceType
from sdbus import sd_bus_open_system
from asyncio import run as async_run

HIDDEN_SSID_STRING = "<***hidden***>"

async def get_ethernet_devices(interface=None):
    """
    Asynchronously retrieves a list of managed Ethernet network devices.

    Args:
        interface (str, optional): The name of a specific network interface to filter the devices. 
            If provided, only devices matching this interface name are returned.

    Returns:
        list: A list of NetworkDeviceWired objects representing managed Ethernet devices. 
            If 'interface' is specified, only devices with the matching interface name are included.

    Raises:
        Any exceptions raised by network_manager.get_devices() or device property access.
    """
    all_devices = await network_manager.get_devices()
    ethernet_devices = []
    for device_path in all_devices:
        device = NetworkDeviceWired(device_path)
        device_type = await device.device_type
        device_managed = await device.managed
        if device_type == DeviceType.ETHERNET and device_managed:
            ethernet_devices.append(device)
    if interface:
        ethernet_devices = [d for d in ethernet_devices if (await d.interface) == interface]
    return ethernet_devices

async def get_wifi_devices(interface=None):
    """
    Asynchronously retrieves a list of managed Wi-Fi network devices.

    Args:
        interface (str, optional): The name of a specific network interface to filter the devices. 
            If provided, only devices matching this interface name are returned.

    Returns:
        list: A list of NetworkDeviceWireless objects representing managed Wi-Fi devices. 
            If 'interface' is specified, only devices with the matching interface name are included.

    Raises:
        Any exceptions raised by network_manager.get_devices() or device property access.
    """
    all_devices = await network_manager.get_devices()
    wifi_devices = []
    for device_path in all_devices:
        device = NetworkDeviceWireless(device_path)
        device_type = await device.device_type
        device_managed = await device.managed
        if device_type == DeviceType.WIFI and device_managed:
            wifi_devices.append(device)
    if interface:
        wifi_devices = [d for d in wifi_devices if (await d.interface) == interface]
    return wifi_devices

async def list_connections():
    """
    List all saved network connections using NetworkManager.
    Returns:
        List of dicts with connection name, UUID, and type.
    """
    networwork_manager_settings = NetworkManagerSettings()
    connections = []
    for connection_path in await networwork_manager_settings.connections:
        connection = NetworkConnectionSettings(connection_path)
        settings = await connection.get_settings()
        connections.append({
            'name': settings['connection']['id'],
            'uuid': settings['connection']['uuid'],
            'type': settings['connection']['type']
        })
    return connections

async def create_new_wifi_connection(ssid, password, interface=None):
    """
    Create a new WiFi connection using NetworkManager.
    Args:
        ssid (bytes): SSID of the WiFi network (as bytes).
        password (str): Password for the WiFi network.
        interface (str): Name of the WiFi interface (optional).
    Returns:
        True if creation is successful, False otherwise.
    """

    wifi_devices = await get_wifi_devices(interface)

    print("Found " + str(len(wifi_devices)) + " Wi-Fi devices")
                
    if interface:
        wifi_devices = [d for d in wifi_devices if d.interface == interface]
    if not wifi_devices:
        print("No Wi-Fi devices found")
        return False
    
    if interface is None:
        # Iterate over all wifi_devices and try to find an AP with matching SSID
        ap = None
        for device in wifi_devices:
            ap_paths = await device.access_points
            for ap_path in ap_paths:
                candidate_ap = AccessPoint(ap_path)
                candidate_ssid = await candidate_ap.ssid
                if candidate_ssid and candidate_ssid == ssid:
                    ap = candidate_ap
                    interface = await device.interface
                    break
            if ap:
                print(f"Found access point for SSID {ssid} on interface {await device.interface}")
                break    
    
    if interface is None:
        print(f'Failed to determine interface for SSID {ssid}')
        return False
    
    try:
        connection_params = {
            'connection': {
                "id": ("s", ssid.decode('utf-8')),
                "uuid": ("s", str(uuid.uuid4())),
                "type": ("s", "802-11-wireless"),
                "interface-name": ("s", await device.interface),
                "autoconnect": ("b", True),
            },            
            '802-11-wireless': {
                "ssid": ("ay", ssid),
                'mode': ("s", 'infrastructure'),
                'security': ("s", '802-11-wireless-security'),
            },
            '802-11-wireless-security': {
                'key-mgmt': ("s", 'wpa-psk'),
                'psk': ("s", password),
            },   
            'ipv4': {
                'method': ("s", 'auto'),
            },
            'ipv6': {
                'method': ("s", 'ignore'),
            },

        }

        network_manager_settings = NetworkManagerSettings()
        new_connection_path = await network_manager_settings.add_connection(connection_params)
        print(f"Created new connection {ssid} at {new_connection_path}")
        return True
    except Exception as e:
        print(f"Failed to create new connection {ssid}: {e}")
        return False
    
async def wifi_connect (ssid, password, interface=None):
    """
    Connect to a WiFi network using NetworkManager.
    Args:
        ssid (str): SSID of the WiFi network.
        password (str): Password for the WiFi network.
        interface (str): Name of the WiFi interface (optional).
    Returns:
        True if connection is successful, False otherwise.
    """
    wifi_devices = await get_wifi_devices(interface)

                
    if interface:
        wifi_devices = [d for d in wifi_devices if d.interface == interface]
    if not wifi_devices:
        return False
    
    # Iterate over all wifi_devices and try to find an AP with matching SSID
    ap = None
    for device in wifi_devices:
        ap_paths = await device.access_points
        for ap_path in ap_paths:
            candidate_ap = AccessPoint(ap_path)
            candidate_ssid = await candidate_ap.ssid
            if candidate_ssid and candidate_ssid.decode('utf-8') == ssid:
                ap = candidate_ap
                break
        if ap:
            break
        
        try:
            # Connect using sdbus_async.networkmanager
            await device    
            await device.connect(ap, password)
            return True
        except Exception as e:
            print(f"Failed to connect to {ssid}: {e}")
            return False

    if ap is None:
        print(f"Failed to connect to {ssid}: Access point not found.")
        return False


async def activate_wifi_connection(ssid, interface=None):
    """
    Activate a WiFi connection using NetworkManager.
    Args:
        ssid (bytes): SSID of the WiFi network to activate (as bytes).
        interface (str, optional): Name of the WiFi interface to use. If None, uses the first available WiFi device.
    Returns:
        bool: True if activation is successful, False otherwise.
    """
    wifi_devices = await get_wifi_devices(interface)

    if interface:
        wifi_devices = [d for d in wifi_devices if (await d.interface) == interface]
    if not wifi_devices:
        print("No Wi-Fi devices found")
        return False
    device = wifi_devices[0]
    try:
        # Find connection with matching SSID
        network_manager_settings = NetworkManagerSettings()
        for connection_path in await network_manager_settings.connections:
            connection = NetworkConnectionSettings(connection_path)
            settings = await connection.get_settings()
            print(settings['connection']['type'])
            if settings['connection']['type'] ==  ("s", "802-11-wireless"):
                print(f"Found Wi-Fi connection: {settings['connection']['id']} with SSID {settings['802-11-wireless']['ssid']}")
                if settings['802-11-wireless']['ssid'] == ("ay", ssid):
                    print(f"Using connection {settings['connection']['id']} for SSID {ssid}")
                    try:
                        # Activate the connection
                        await network_manager.activate_connection(connection_path, "/", "/")
                        print(f"Activated connection for SSID {ssid} on interface {await device.interface}")
                        return True
                    except Exception as e:
                        print(f"Failed to activate connection {ssid}: {e}")
                        return False

        print(f"Connection with SSID '{ssid}' not found.")
        return False

    except Exception as e:
        print(f"Error while attempting to activate connection {ssid}: {e}")
        return False
  
def list_all_connections():
    """
    List all saved network connections using NetworkManager.
    Returns:
        List of dicts with connection name, UUID, and type.
    """
    connections = []
    for connection_path in network_manager.settings.ConnectionSettings:
        connection = NetworkConnectionSettings(connection_path)
        settings = connection.get_settings()
        connections.append({
            'name': settings['connection']['id'],
            'uuid': settings['connection']['uuid'],
            'type': settings['connection']['type']
        })
    return connections

async def filter_network_list(network_list, unique_ssids=False, best_signal=False, show_hidden=False):
    """
    Filter the list of WiFi networks.
    Args:
        network_list (list): List of WiFi networks to filter.
        unique_ssids (bool): If True, only keep networks with unique SSIDs.
        best_signal (bool): If True, only keep the network with the best signal strength for each SSID.

    Returns:
        list: Filtered list of WiFi networks.
    """
    if unique_ssids:
        seen_ssids = set()
        filtered = []
        for net in network_list:
            ssid = net['ssid']
            if ssid == HIDDEN_SSID_STRING:
                if show_hidden:
                    filtered.append(net)
                continue  # skip hidden if show_hidden is False
        for net in network_list:
            ssid = net['ssid']
            if best_signal:
                # Only keep the network with the best signal strength for each SSID
                if ssid not in seen_ssids:
                    seen_ssids.add(ssid)
                    filtered.append(net)
                else:
                    # Find and replace if this net has better signal
                    for i, existing in enumerate(filtered):
                        if existing['ssid'] == ssid and net['strength'] > existing['strength']:
                            filtered[i] = net
                            break
            else:
                if ssid not in seen_ssids:
                    seen_ssids.add(ssid)
                    filtered.append(net)
            if ssid not in seen_ssids:
                seen_ssids.add(ssid)
                filtered.append(net)
        return filtered
    return network_list

async def list_wifi_networks(interface=None):
    """
    List available WiFi networks using python-sdbus-networkmanager (async).
    Args:
        interface (str): Name of the WiFi interface (optional).
    Returns:
        List of dicts with SSID, BSSID, and signal strength.
    """
    print("Listing WiFi networks...")
    all_devices = await network_manager.get_devices()
    print("Found " + str(len(all_devices)) + " devices")
    wifi_devices = []
    for device_path in all_devices:
        device = NetworkDeviceWireless(device_path)
        device_type = await device.device_type
        if device_type == DeviceType.WIFI:
            wifi_devices.append(device)
    if interface:
        wifi_devices = [d for d in wifi_devices if (await d.interface) == interface]
    results = []
    for wifi_device in wifi_devices:
        ap_paths = await wifi_device.get_all_access_points()
        print(f"Found {len(ap_paths)} access points on interface {await wifi_device.interface}")
        for ap_path in ap_paths:
            ap_interface = AccessPoint(ap_path)
            ssid = await ap_interface.ssid
            if not ssid:
                ssid = HIDDEN_SSID_STRING
            else:
                ssid = ssid.decode('utf-8')
            results.append({
                'ssid': ssid,
                'bssid': await ap_interface.hw_address,
                'strength': await ap_interface.strength
            })
    return results
      


async def scan_wifi_networks(interface=None, timeout=60, result_age_limit=30):
    """
    Initiate a WiFi scan using python-sdbus-networkmanager (async) and wait for scan results.
    Args:
        interface (str, optional): WiFi interface name to scan. If None, scans all WiFi interfaces.
        timeout (int, optional): Maximum time to wait for scan completion (seconds).
        result_age_limit (int, optional): Minimum seconds since last scan before requesting a new scan.
    Returns:
        list: List of dicts with SSID, BSSID, and signal strength for each detected network.
    """
    
    wifi_devices = await get_wifi_devices(interface)
   
    for device in wifi_devices:
        last_scan_time = int(await device.last_scan / 1000)
        current_time = int(time.monotonic())
        if last_scan_time == -1 or (current_time - last_scan_time > result_age_limit):
            print(f"It has been {current_time - last_scan_time} seconds since last scan time for {await device.interface}: {last_scan_time}, current time: {current_time}")
            print(f"Requesting scan on interface {await device.interface} ...")
            try:
                # Wait for a scan to complete, the device to become available for a new scan or until timeout
                start_time = time.time()
                while True:
                    state = await device.state
                    last_scan_time = int(await device.last_scan / 1000)
                    current_time = int(time.monotonic())
                    print(f"It has been {current_time - last_scan_time} seconds since last scan time for {await device.interface}: {last_scan_time}, current time: {current_time}")
                    if (current_time - last_scan_time <= result_age_limit):
                        break
                    if state == 100:  # NM_DEVICE_STATE_ACTIVATED
                        break
                    if time.time() - start_time > timeout:
                        print(f"Timeout waiting for device {await device.interface} to become available.")
                        return []
                    await asyncio.sleep(1)
                await device.request_scan({})
                print("Scan requested successfully.")
                # Wait for scan to complete before listing networks
                scan_complete = False
                start_scan_time = time.time()
                while not scan_complete:
                    # Check if scan results are available (last_scan updated)
                    updated_last_scan_time = await device.last_scan
                    if updated_last_scan_time and updated_last_scan_time > last_scan_time:
                        scan_complete = True
                        break
                    if time.time() - start_scan_time > timeout:
                        print(f"Timeout waiting for scan results on {await device.interface}.")
                        return []
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Failed to request scan: {e}")
                return []
        else:
            print(f"Skipping scan request for {await device.interface}: last scan was {current_time - last_scan_time} seconds ago.")
    return await list_wifi_networks()


async def get_wired_network_info(interface=None):
    """
    Get information about wired network interfaces.
    Args:
        interface (str): Name of the wired interface (optional).
    Returns:
        List of dicts with interface name, MAC address, and IP addresses.
    """

    print("Calling get_ethernet_devices...")
    # ethernet_devices = await get_ethernet_devices(interface)
    print("Getting all devices from NetworkManager...")
    all_devices = await network_manager.get_devices()
    print(f"Total devices found: {len(all_devices)}")
    ethernet_devices = []
    for device_path in all_devices:
        print(f"Processing device path: {device_path}")
        device = NetworkDeviceWired(device_path)
        try:
            device_type = await asyncio.wait_for(device.device_type, timeout=2)
            print(f"  Device type: {device_type}")
            device_managed = await asyncio.wait_for(device.managed, timeout=2)
            print(f"  Device managed: {device_managed}")
            if device_type == DeviceType.ETHERNET and device_managed:
                print(f"  -> Adding ethernet device: {device_path}")
                ethernet_devices.append(device)
        except asyncio.TimeoutError:
            print(f"  Timeout waiting for device_type or managed for {device_path}, skipping device.")
        except Exception as e:
            print(f"  Error getting device_type or managed for {device_path}: {e}, skipping device.")
    if interface:
        print(f"Filtering ethernet devices for interface: {interface}")
        ethernet_devices = [d for d in ethernet_devices if (await d.interface) == interface]
    print(f"Ethernet devices after filtering: {[await d.interface for d in ethernet_devices]}")

    print(f"Got {len(ethernet_devices)} ethernet devices")

    if interface:
        print(f"Filtering for interface: {interface}")
        ethernet_devices = [d for d in ethernet_devices if d.interface == interface]

    print("Ethernet devices:", [await d.interface for d in ethernet_devices])

    results = []
    for device in ethernet_devices:
        print(f"Processing device: {device}")
        print("  Awaiting device.ip4_config...")
        ip4_conf_path = await device.ip4_config
        print(f"  ip4_conf_path: {ip4_conf_path}")
        addresses = []
        if ip4_conf_path and ip4_conf_path != '/':
            print(f"  Creating IPv4Config for {ip4_conf_path}")
            ip4_conf = IPv4Config(ip4_conf_path)
            print("  Awaiting ip4_conf.address_data...")
            address_data_list = await ip4_conf.address_data
            print(f"  Got address_data_list: {address_data_list}")
            for address_data in address_data_list:
                print(f"    Address data: {address_data}")
                addresses.append(f"{address_data['address'][1]}/{address_data['prefix'][1]}")
        print("  Awaiting device.interface...")
        iface = await device.interface
        print(f"  Interface: {iface}")
        print("  Awaiting device.hw_address...")
        mac = await device.hw_address
        print(f"  MAC address: {mac}")
        results.append({
            'interface': iface,
            'mac_address': mac,
            'ip_addresses': addresses
        })
    print(f"Returning results: {results}")
    return results

async def get_wireless_network_info(interface=None):
    """
    Get information about wireless network interfaces.
    Args:
        interface (str): Name of the wireless interface (optional).
    Returns:
        List of dicts with interface name, MAC address, SSID, and IP addresses.
    """
    all_devices = await network_manager.get_devices()
    wifi_devices = []
    for device_path in all_devices:
        device = NetworkDeviceGeneric(device_path)
        device_type = await device.device_type
        if device_type == DeviceType.WIFI:
            wifi_devices.append(device)
    if interface:
        wifi_devices = [d for d in wifi_devices if (await d.interface) == interface]
    print("Wi-Fi devices:", [await d.interface for d in wifi_devices])
    results = []
    for device in wifi_devices:
        ip4_conf_path = await device.ip4_config
        addresses = []
        if ip4_conf_path and ip4_conf_path != '/':
            ip4_conf = IPv4Config(ip4_conf_path)
            for address_data in await ip4_conf.address_data:
                addresses.append(f"{address_data['address'][1]}/{address_data['prefix'][1]}")
        ssid = None
        ap = getattr(device, 'active_access_point', None)
        if ap is not None:
            ssid = getattr(ap, 'ssid', None)
        results.append({
            'interface': await device.interface,
            'mac_address': await device.hw_address,
            'ssid': ssid,
            'ip_addresses': addresses
        })
    return results

   
    
sdbus.set_default_bus(sdbus.sd_bus_open_system())
network_manager = NetworkManager()

async def test() -> None:

    try:
        wired_interfaces = await get_wired_network_info()
        for iface in wired_interfaces:
            print(iface)
    except Exception as e:
        print(f"Error getting wired network info: {e}")
        
    try:
        wifi_interfaces = await get_wireless_network_info()
        for iface in wifi_interfaces:
            print(iface)
    except Exception as e:
        print(f"Error getting wireless network info: {e}")
        
    try: 
        wifi_network_list = await scan_wifi_networks()
        print("Number of networks found:", len(wifi_network_list))
        for net in wifi_network_list:
            print(net)
        filtered_network_list = await filter_network_list(wifi_network_list, unique_ssids=True, best_signal=True, show_hidden=False)
        print("Number of filtered networks:", len(filtered_network_list))
        for net in filtered_network_list:
            print(net)
    except Exception as e:
        print(f"Error scanning WiFi networks: {e}") 
        available_networks = await list_wifi_networks()
        print("Found " + str(len(available_networks)) + " networks")
        for net in available_networks:
            print(net)
    except Exception as e:
        print(f"Error listing WiFi networks: {e}")
        
    # try: 
    #     await create_new_wifi_connection(ssid=b'Cargt Guest', password='J+P4evEr')
    # except Exception as e: 
    #     print(f"Error creating new connection: {e}")
        
    # try:
    #     connections = await list_connections()
    #     for connection in connections:
    #         print(connection)
    # except Exception as e:
    #     print(f"Error listing connections: {e}")
        
    # try:
    #     await activate_wifi_connection(ssid=b'Cargt Guest')
    # except Exception as e: 
    #     print(f"Error activating connection: {e}")
    

# async_run(test())