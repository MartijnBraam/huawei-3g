# Huawei 3G python module
[![Build Status](https://travis-ci.org/MartijnBraam/huawei-3g.svg)](https://travis-ci.org/MartijnBraam/huawei-3g)
[![Coverage Status](https://coveralls.io/repos/MartijnBraam/huawei-3g/badge.svg?branch=master&service=github)](https://coveralls.io/github/MartijnBraam/huawei-3g?branch=master)

A python module for controlling Huawei 3G usb modems. At the moment it only supports the Huawei E303 usb dongle since that's
the only one I own.

## Features

- [x] Find all Huawei modems and associated network interface
- [ ] Get modem status
- [ ] Connect/disconnect internet
- [ ] Change sim settings
- [ ] Get SMS messages
- [ ] Send SMS messages

## Usage example

```python
>>> from huawei_3g import modem as modem
>>>modem.find()
[
    {
        'name': 'Huawei E303',
        'interface': 'enp0s20u1',
        'path': '/sys/bus/usb/devices/1-1',
        'supported': True,
        'class': 'huawei_e303',
        'productId': '14dc'
    }
]

>>>modem.load()
[<HuaweiE303Modem enp0s20u1 (/sys/bus/usb/devices/1-1)>]
```