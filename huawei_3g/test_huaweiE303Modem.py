from unittest import TestCase
from huawei_3g.huawei_e303 import HuaweiE303Modem, TokenError
import requests
import responses
import datetime


class TestHuaweiE303Modem(TestCase):
    @responses.activate
    def test_get_status(self):
        payload = ""
        with open("fixtures/status.xml") as payload_file:
            payload = payload_file.read()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://192.168.8.1/api/monitoring/status',
            'body': payload,
            'status': 200
        })

        modem = HuaweiE303Modem('eth0', '/')
        status = modem.get_status()
        self.assertDictEqual(status, {
            'status': 'Connected',
            'signal': 40,
            'network_type': 'GPRS'
        })

    @responses.activate
    def test_get_message_count(self):
        payload = ""
        with open("fixtures/sms-count.xml") as payload_file:
            payload = payload_file.read()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://192.168.8.1/api/sms/sms-count',
            'body': payload,
            'status': 200
        })
        modem = HuaweiE303Modem('eth0', '/')
        messages = modem.get_message_count()
        self.assertDictEqual(messages, {
            'count': 2,
            'unread': 1
        })

    @responses.activate
    def test_get_messages(self):
        with open("fixtures/sms-list-2.xml") as payload_file:
            payload = payload_file.read()
        responses.add(**{
            'method': responses.POST,
            'url': 'http://192.168.8.1/api/sms/sms-list',
            'body': payload,
            'status': 200
        })
        modem = HuaweiE303Modem('eth0', '/')
        messages = modem.get_messages(delete=False)
        self.assertEqual(len(messages), 2)

        message = messages[0]
        self.assertEqual(message.message_id, '40001')
        self.assertEqual(message.message, 'Test 2')
        self.assertEqual(message.sender, '+31617000000')
        self.assertEqual(message.receive_time, datetime.datetime(2015, 9, 8, 11, 3, 23))

        message = messages[1]
        self.assertEqual(message.message_id, '40000')
        self.assertEqual(message.message, 'Test')
        self.assertEqual(message.sender, '+31617000000')
        self.assertEqual(message.receive_time, datetime.datetime(2015, 9, 8, 11, 3))

    @responses.activate
    def test_get_single_message(self):
        """
        This is tested separately because the format for a single message is different
        This is a side effect of the XML parser used.
        :return:
        """
        with open("fixtures/sms-list-1.xml") as payload_file:
            payload = payload_file.read()
        responses.add(**{
            'method': responses.POST,
            'url': 'http://192.168.8.1/api/sms/sms-list',
            'body': payload,
            'status': 200
        })
        modem = HuaweiE303Modem('eth0', '/')
        messages = modem.get_messages(delete=False)
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message.message_id, '40000')
        self.assertEqual(message.message, 'Test')
        self.assertEqual(message.sender, '+31617000000')
        self.assertEqual(message.receive_time, datetime.datetime(2015, 9, 8, 11, 3))

    def test_delete_message(self):
        self.assertTrue(True)

    def test_delete_messages(self):
        self.assertTrue(True)

    @responses.activate
    def test__get_token(self):
        responses.add(**{
            'method': responses.GET,
            'url': 'http://192.168.8.1/api/webserver/token',
            'body': '<response><token>1</token></response>',
            'status': 200
        })

        modem = HuaweiE303Modem('eth0', '/')
        modem._get_token()
        self.assertEqual(modem.token, '1')

    @responses.activate
    def test__api_get(self):
        """
        My huawei E303 never fails on a missing token when using GET requests but huawei might change this behavior
        so I test this anyway
        :return:
        """
        responses.add(**{
            'method': responses.GET,
            'url': 'http://192.168.8.1/api/webserver/token',
            'body': '<response><token>2</token></response>',
            'status': 200
        })

        def api_need_token_response(request):
            if '__RequestVerificationToken' in request.headers and request.headers['__RequestVerificationToken'] == '2':
                return (200, {}, '<response><testresult>success</testresult></response>')
            else:
                # Yes errors have http status 200 with this dongle
                return (200, {}, '<error><code>125001</code></error>')

        responses.add_callback(**{
            'method': responses.GET,
            'url': 'http://192.168.8.1/api/test',
            'callback': api_need_token_response,
        })

        modem = HuaweiE303Modem('eth0', '/')
        response = modem._api_get('/test')
        self.assertDictEqual(response, {'testresult': 'success'})
        self.assertEqual(modem.token, '2')

    @responses.activate
    def test__api_post(self):
        responses.add(**{
            'method': responses.GET,
            'url': 'http://192.168.8.1/api/webserver/token',
            'body': '<response><token>2</token></response>',
            'status': 200
        })

        def api_need_token_response(request):
            if '__RequestVerificationToken' in request.headers and request.headers['__RequestVerificationToken'] == '2':
                return (200, {}, '<response><testresult>success</testresult></response>')
            else:
                # Yes errors have http status 200 with this dongle
                return (200, {}, '<error><code>125001</code></error>')

        responses.add_callback(**{
            'method': responses.POST,
            'url': 'http://192.168.8.1/api/test',
            'callback': api_need_token_response,
        })

        modem = HuaweiE303Modem('eth0', '/')
        response = modem._api_post('/test', 'payload')
        self.assertDictEqual(response, {'testresult': 'success'})
        self.assertEqual(modem.token, '2')

    def test__parse_api_response(self):
        test_cases = [
            {
                'response': '<response><testresult>success</testresult></response>',
                'success': True,
                'message': {'testresult': 'success'}
            },
            {
                'response': '<response><a>1</a><b>2</b><c><d>3</d></c></response>',
                'success': True,
                'message': {
                    'a': '1',
                    'b': '2',
                    'c': {
                        'd': '3'
                    }
                }
            },
            {
                'response': '<error><code>100002</code></error>',
                'success': False,
                'error': 100002,
                'message': 'No support'
            },
            {
                'response': '<error><code>1337</code></error>',
                'success': False,
                'error': 1337,
                'message': 'Unknown error occurred'
            },
            {
                'response': '<error><code>125001</code></error>',
                'success': False,
                'error': 125001,
                'message': 'Token error'
            }
        ]
        modem = HuaweiE303Modem('eth0', '/')
        for case in test_cases:
            request_object = requests.Response()
            request_object._content = case['response']
            request_object.status_code = 200

            if case['success']:
                result = modem._parse_api_response(request_object)
                self.assertDictEqual(case['message'], result)
            else:
                try:
                    modem._parse_api_response(request_object)
                except TokenError:
                    self.assertEqual(case['error'], 125001)
                except Exception as error:
                    self.assertEqual(case['message'], str(error))
