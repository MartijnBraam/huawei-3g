import glob
import os.path


def find():
    """
    Get a list of Huawei dongles attached to this computer

    This reads files in sysfs (/sys/**) to determine which usb devices are attached and then filters on vendor
    id and product id.

    This returns a list of dictionaries. Each dictionary contains information about a single attached modem.

    The keys of the dictionary:

    path
      The path of the device in sysfs like /sys/bus/usb/devices/1-1

    supported
      A boolean indicating that this modem is supported by this Python module

    productId
      The USB product id of the modem as a string. Ex: 14dc

    interface
      The network interface associated with this modem as tring. Ex: eth0 or enp0s3b4

    If the modem is supported by this module the following keys also exist in the dictionary:

    name
      The product name of the dongle. Ex: Huawei E303

    class
      The class in this Python module that implements the interface with this modem.
    """
    huawei_vendor = "12d1"
    result = []
    supported_dongles = {
        "14dc": {
            "name": "Huawei E303",
            "class": "huawei_e303"
        }
    }
    for device in glob.glob("/sys/bus/usb/devices/*/idVendor"):
        with open(device) as vendor_file:
            vendor_id = vendor_file.read().strip()
        if vendor_id == huawei_vendor:
            path_part = device.split("/")
            sysfs_path = "/".join(path_part[0:-1])

            with open(os.path.join(sysfs_path, "idProduct")) as product_file:
                product_id = product_file.read().strip()

            if product_id in supported_dongles:
                result.append({
                    "path": sysfs_path,
                    "supported": True,
                    "productId": product_id,
                    "name": supported_dongles[product_id]["name"],
                    "class": supported_dongles[product_id]["class"],
                    "interface": find_interface(sysfs_path)
                })
            else:
                result.append({
                    "path": sysfs_path,
                    "supported": False,
                    "productId": product_id,
                    "interface": find_interface(sysfs_path)
                })
    return result


def find_interface(sysfs_device_path):
    """ Find the network interface associated with a sysfs device path

    :param sysfs_device_path: The sysfs path to a plugged in modem like /sys/devices/pci0000:00/0000:00:1c.3/0000:02:00.0
    :return: the network interface. Ex: eth0
    """
    sysfs_device = os.path.realpath(sysfs_device_path)
    for interface in glob.glob("/sys/class/net/*"):
        device_symlink = os.path.join(interface, "device")
        device_endpoint = os.path.realpath(device_symlink)
        if sysfs_device in device_endpoint:
            return os.path.basename(interface)
    return None


def load():
    """ Find all supported Huawei modem and return a list of modem objects

    This uses :func:`~huawei_3g.find` to search for all the modems on the computer and creates the class instances
    for all modems and returns that as a list
    :return: list of modem classes
    """
    result = []
    modems = find()
    for modem in modems:
        if modem['supported']:
            if modem['class'] == 'huawei_e303':
                import huawei_3g.huawei_e303
                result.append(huawei_3g.huawei_e303.HuaweiE303Modem(modem["interface"], modem["path"]))
    return result
