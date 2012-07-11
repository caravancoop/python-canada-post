from canada_post.util import InfoObject

class AddressBase(InfoObject):
    def __init__(self, postal_code, **kwargs):
        self.postal_code = postal_code.replace(" ", "")
        super(AddressBase, self).__init__(**kwargs)

class Origin(AddressBase):
    pass

class Destination(AddressBase):
    def __init__(self, postal_code, country_code, **kwargs):
        self.country_code = country_code
        super(Destination, self).__init__(postal_code=postal_code, **kwargs)