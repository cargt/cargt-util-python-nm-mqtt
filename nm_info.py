import sdbus

from sdbus_block.networkmanager import (
    NetworkDeviceGeneric,
    NetworkDeviceWireless,
    NetworkDeviceWired,
    NetworkManager,
    IPv4Config,
)
from sdbus_block.networkmanager.enums import DeviceType

sdbus.set_default_bus(sdbus.sd_bus_open_system())
network_manager = NetworkManager()

all_devices = {path: NetworkDeviceGeneric(path) for path in network_manager.devices}

wifi_devices = [
    NetworkDeviceWireless(path)
    for path, device in all_devices.items()
    if device.device_type == DeviceType.WIFI
]

ethernet_devices = [
    NetworkDeviceWired(path)
    for path, device in all_devices.items()
    if device.device_type == DeviceType.ETHERNET
]

print ('Ethernet devices')
for device in ethernet_devices:
    print(device.interface, ' [', device.hw_address, ']', )
    device_ip4_conf_path = device.ip4_config
    ip4_conf = IPv4Config(device_ip4_conf_path)
    for address_data in ip4_conf.address_data:
        if device_ip4_conf_path == '/':
            # This is how NetworkManager indicates there is no ip config
            # for the interface
            continue
        else:
            ip4_conf = IPv4Config(device_ip4_conf_path)
            for address_data in ip4_conf.address_data:
                print('     ', address_data['address'][1], '/', address_data['prefix'][1])

print ('WiFi devices')
for device in wifi_devices:
    print(device.interface, ' [', device.hw_address, ']', )
    device_ip4_conf_path = device.ip4_config
    ip4_conf = IPv4Config(device_ip4_conf_path)
    for address_data in ip4_conf.address_data:
        if device_ip4_conf_path == '/':
            # This is how NetworkManager indicates there is no ip config
            # for the interface
            continue
        else:
            ip4_conf = IPv4Config(device_ip4_conf_path)
            for address_data in ip4_conf.address_data:
                print('     ', address_data['address'][1], '/', address_data['prefix'][1])

