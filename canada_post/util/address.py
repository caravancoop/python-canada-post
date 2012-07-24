from canada_post.util import InfoObject

class AddressBase(InfoObject):
    def __init__(self, postal_code, name=None, company=None, **kwargs):
        self.postal_code = postal_code.replace(" ", "")
        self.name = name
        self.company = company
        super(AddressBase, self).__init__(**kwargs)

class Origin(AddressBase):
    def __init__(self, phone=None, *args, **kwargs):
        self.phone = phone
        super(Origin, self).__init__(*args, **kwargs)

class Destination(AddressBase):
    def __init__(self, country_code, *args, **kwargs):
        self.country_code = country_code
        super(Destination, self).__init__(*args, **kwargs)
