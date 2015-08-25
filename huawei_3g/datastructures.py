class SMSMessage:
    message = ""
    sender = ""
    receive_time = None

    def __repr__(self):
        return "<SMSMessage '{}' from '{}'>".format(self.message, self.sender)