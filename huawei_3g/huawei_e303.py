import requests
import xmltodict
from huawei_3g.datastructures import SMSMessage


class HuaweiE303Modem:
    token = ""

    def __init__(self, interface, sysfs_path):
        self.interface = interface
        self.path = sysfs_path
        self.ip = "192.168.8.1"
        self.base_url = "http://{}/api".format(self.ip)
        self.token = ""
        token_response = self._api_get("/webserver/token")
        self.token = token_response['token']

    def get_status(self):
        status_raw = self._api_get("/monitoring/status")
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

    def get_message_count(self):
        messages_raw = self._api_get("/sms/sms-count")
        return {
            'count': int(messages_raw['LocalInbox']),
            'unread': int(messages_raw['LocalUnread'])
        }

    def get_messages(self):
        raw = self._api_post("/sms/sms-list",
                             "<?xml version=\"1.0\" encoding=\"UTF-8\"?><request><PageIndex>1</PageIndex><ReadCount>20</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>0</UnreadPreferred></request>")
        messages = []
        for message in raw['Messages']['Message']:
            sms = SMSMessage()
            sms.message = message['Content']
            sms.sender = message['Phone']
            sms.receive_time = message['Date']
            messages.append(sms)
        return messages

    def __repr__(self):
        return "<HuaweiE303Modem {} ({})>".format(self.interface, self.path)

    def _api_get(self, url):
        url = self.base_url + url
        response = requests.get(url)
        return self._parse_api_response(response)

    def _api_post(self, url, parameters):
        url = self.base_url + url
        parameters = parameters.encode('UTF-8')

        response = requests.post(url, parameters, headers={
            "__RequestVerificationToken": self.token
        })
        return self._parse_api_response(response)

    def _parse_api_response(self, response):
        if response.status_code == 200:
            payload = response.content
            parsed = xmltodict.parse(payload)
            if 'response' in parsed:
                return parsed['response']
            else:
                raise Exception("Reponse error")
        return {}
