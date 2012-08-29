class InfoObject(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
        # set any extra kwargs we got
            setattr(self, k, v)

    def __repr__(self):
        return u"{klass}.{contents}".format(klass=self.__class__.__name__,
                                            contents=repr(self.__dict__))
