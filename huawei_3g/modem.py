import glob
import os.path


def find():
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
    sysfs_device = os.path.realpath(sysfs_device_path)
    for interface in glob.glob("/sys/class/net/*"):
        device_symlink = os.path.join(interface, "device")
        device_endpoint = os.path.realpath(device_symlink)
        if sysfs_device in device_endpoint:
            return os.path.basename(interface)
    return None


def load():
    result = []
    modems = find()
    for modem in modems:
        if modem['supported']:
            if modem['class'] == 'huawei_e303':
                import huawei_3g.huawei_e303
                result.append(huawei_3g.huawei_e303.HuaweiE303Modem(modem["interface"], modem["path"]))
    return result