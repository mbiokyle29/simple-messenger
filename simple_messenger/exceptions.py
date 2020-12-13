''' exceptions.py '''


class SimpleMessengerException(Exception):

    def __init__(self, message, status, status_code):
        self.message = message
        self.status = status
        self.status_code = status_code
