from canada_post.util import InfoObject

class AddressBase(InfoObject):
    def __init__(self, postal_code, **kwargs):
        self.postal_code = postal_code.replace(" ", "")
        super(InfoObject, self).__init__(**kwargs)

class Origin(AddressBase):
    pass

class Destination(AddressBase):
    pass