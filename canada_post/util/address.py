from canada_post.util import InfoObject

class AddressBase(InfoObject):
    def __init__(self, postal_code, name=None, company=None, phone=None,
                 address=None, city=None, province=None,
                 *args, **kwargs):
        self.postal_code = postal_code.replace(" ", "").upper()
        self.name = name
        self.company = company
        self.phone = phone

        if address:
            if isinstance(address, tuple):
                assert all(len(x) < 44 for x in address), ("Street address "
                                                           "must be split in "
                                                           "two 44 characters "
                                                           "groups")
                self.address1 = address[0]
                self.address2 = address[1]
            else:
                assert len(address) < 88, ("Street address can have up to 88 "
                                           "characters")
                last_space_ix = address.rfind(" ", 0, 44)
                self.address1 = address[:last_space_ix].strip()
                self.address2 = address[last_space_ix:].strip()
                assert len(self.address2) < 44, ("Must be able to split "
                                                 "address in two 44 characters "
                                                 "groups")
        else:
            self.address1 = self.address2 = None

        self.city = city
        if city:
            assert len(city) < 40, ("City name must have up to 40 characters")

        self.province = province

        assert not args, "Too many positional arguments for {} object".format(
            self.__class__.__name__)
        super(AddressBase, self).__init__(**kwargs)

class Origin(AddressBase):
    def __init__(self, country_code="CA", *args, **kwargs):
        self.country_code = country_code
        super(Origin, self).__init__(*args, **kwargs)

class Destination(AddressBase):
    def __init__(self, country_code, extra=None, *args, **kwargs):
        self.country_code = country_code
        self.extra = extra
        super(Destination, self).__init__(*args, **kwargs)
