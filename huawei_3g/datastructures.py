class SMSMessage:
    """A SMS message received by a modem"""
    message_id = ""
    message = ""
    sender = ""
    receive_time = None

    def __repr__(self):
        return "<SMSMessage {} '{}' from '{}'>".format(self.message_id, self.message, self.sender)