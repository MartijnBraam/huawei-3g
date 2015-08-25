import requests
import xml.etree.ElementTree

class HuaweiE303Modem:
    def __init__(self, interface, sysfs_path):
        self.interface = interface
        self.path = sysfs_path
        self.ip = "192.168.8.1"
        self.base_url = "http://{}/api".format(self.ip)

    def get_status(self):
        status_raw = self._api_get("/monitoring/status", {})
        status_lut = {
            '900': 'connecting',
            '901': 'connected',
            '902': 'disconnected',
            '903': 'disconnecting',
            '905': 'connected'
        }
        signal = int(int(status_raw['SignalIcon']) / 5.0 * 100.0)
        return {
            'status': status_lut[status_raw['ConnectionStatus']],
            'signal': signal
        }


    def __repr__(self):
        return "<HuaweiE303Modem {} ({})>".format(self.interface, self.path)

    def _api_get(self, url, parameters):
        url = self.base_url + url
        response = requests.get(url)
        if response.status_code == 200:
            payload = response.content.decode('utf-8')
            root = xml.etree.ElementTree.fromstring(payload)
            result = {}
            for child in root:
                result[child.tag] = child.text
            return result
        return {}