from unittest import TestCase
from mock import Mock, patch
import huawei_3g.modem as modem
import huawei_3g.huawei_e303


class TestFind(TestCase):
    @patch('builtins.open')
    @patch('glob.glob')
    def test_find(self, mock_glob, mock_open_call):
        mock_glob.return_value = ['/sys/bus/usb/devices/1-5/idVendor', '/sys/bus/usb/devices/1-1/idVendor',
                                       '/sys/bus/usb/devices/1-8/idVendor', '/sys/bus/usb/devices/usb1/idVendor',
                                       '/sys/bus/usb/devices/usb2/idVendor']

        mock_open_call.side_effect = self.open_mocker
        result = modem.find()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['path'], '/sys/bus/usb/devices/1-1')
        self.assertEqual(result[0]['productId'], '14dc')
        self.assertEqual(result[0]['class'], 'huawei_e303')
        self.assertEqual(result[0]['name'], 'Huawei E303')
        self.assertEqual(result[0]['supported'], True)
        self.assertEqual(result[1]['path'], '/sys/bus/usb/devices/1-8')
        self.assertEqual(result[1]['productId'], '15dc')
        self.assertEqual(result[1]['supported'], False)

    @patch('builtins.open')
    @patch('glob.glob')
    def test_load(self, mock_glob, mock_open_call):
        mock_glob.return_value = ['/sys/bus/usb/devices/1-5/idVendor', '/sys/bus/usb/devices/1-1/idVendor',
                                       '/sys/bus/usb/devices/1-8/idVendor', '/sys/bus/usb/devices/usb1/idVendor',
                                       '/sys/bus/usb/devices/usb2/idVendor']

        mock_open_call.side_effect = self.open_mocker
        result = modem.load()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], huawei_3g.huawei_e303.HuaweiE303Modem)

    def open_mocker(self, filename):
        contents = {
            '/sys/bus/usb/devices/1-5/idVendor': '8086',
            '/sys/bus/usb/devices/1-1/idVendor': '12d1',
            '/sys/bus/usb/devices/1-8/idVendor': '12d1',
            '/sys/bus/usb/devices/1-1/idProduct': '14dc',
            '/sys/bus/usb/devices/1-8/idProduct': '15dc',
            '/sys/bus/usb/devices/usb1/idVendor': '8086',
            '/sys/bus/usb/devices/usb2/idVendor': '8086'
        }
        if filename not in contents:
            raise FileNotFoundError(filename)

        mock_file_handle = Mock()
        mock_file_handle.read = Mock(return_value=contents[filename])

        mock_object = Mock()
        mock_object.__enter__ = Mock(return_value=mock_file_handle)
        mock_object.__exit__ = Mock(return_value=False)
        return mock_object
