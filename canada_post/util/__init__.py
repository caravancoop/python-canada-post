class InfoObject(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
        # set any extra kwargs we got
            setattr(self, k, v)
