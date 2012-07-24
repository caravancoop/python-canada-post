from canada_post.util import InfoObject

class AddressBase(InfoObject):
    def __init__(self, postal_code, name=None, company=None, phone=None,
                 address=None, city=None, province=None,
                 *args, **kwargs):
        self.postal_code = postal_code.replace(" ", "")
        self.name = name
        self.company = company
        self.phone = phone


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
