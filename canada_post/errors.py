class CanadaPostError(Exception):
    """
    Base exception class for Canada Post
    """
    def __init__(self, code, message, *args, **kwargs):
        self.code = code
        self.message = message
        super(CanadaPostError, self).__init__(*args, **kwargs)

def Wait(Exception):
    pass
