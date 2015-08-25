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
                    "class": supported_dongles[product_id]["class"]
                })
            else:
                result.append({
                    "path": sysfs_path,
                    "supported": False,
                    "productId": product_id
                })
    return result