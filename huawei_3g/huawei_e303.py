class HuaweiE303Modem:
    def __init__(self, interface, sysfs_path):
        self.interface = interface
        self.path = sysfs_path

    def __repr__(self):
        return "<HuaweiE303Modem {} ({})>".format(self.interface, self.path)
