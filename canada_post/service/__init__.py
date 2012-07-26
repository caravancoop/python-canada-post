"""
Different Canada Post Developer Program services
"""
import logging
from canada_post import DEV, PROD
from canada_post.util.money import Price, get_decimal, Adjustment

class ServiceBase(object):
    """
    base class for API endpoints/services
    """
    SERVER = {
        DEV: "ct.soa-gw.canadapost.ca",
        PROD: "soa-gw.canadapost.ca",
    }

    def __init__(self, auth):
        self.auth = auth

    def get_server(self):
        return self.SERVER[self.auth.dev]

    def userpass(self):
        return self.auth.username, self.auth.password

class Service(object):
    """
    Represents each of the service options returned from a call to GetRates for
    a given parcel. Serves as parameter to call GetService
    """
    log = logging.getLogger('canada_post.service.rating.Service')
    def __init__(self, xml_subtree=None, data={}):
        if xml_subtree is not None:
            self._from_xml(xml_subtree)
        else:
            self.code = data.get('code', 'BAD.CODE')
            self.link = data.get('link', {})
            self.name = data.get('name', 'UNDEFINED')
            self.price = data.get('price', Price())

    def __repr__(self):
        return "Service(data={{ code='{code}', link='{link}', name='{name}', " \
               "price={price} }})".format(code=self.code, link=repr(self.link),
                                         name=self.name, price=repr(self.price))

    def _from_xml(self, xml):
        """
        Initialize instance from the provided XML. It should be an object of
        lxml.etree.Element representing one of CP's response's <price-quote>
        elements
        """
        self.code = xml.find("service-code").text
        self.link = dict(xml.find("service-link").attrib)
        self.name = xml.find("service-name").text
        self.price = self._price_from_xml(xml.find("price-details"))

    def _price_from_xml(self, xml):
        """
        Create a Price detail object from a <price-details> XML element as
        returned from the CP API
        """
        due = get_decimal(xml.find("due").text)
        base = get_decimal(xml.find("base").text)
        tax = xml.find("taxes/gst")
        gst = get_decimal(tax.text)
        gst_percent = get_decimal(tax.get("percent"))
        tax = xml.find("taxes/pst")
        pst = get_decimal(tax.text)
        pst_percent = get_decimal(tax.get("percent"))
        tax = xml.find("taxes/hst")
        hst = get_decimal(tax.text)
        hst_percent = get_decimal(tax.get("percent"))
        adjustments = [Adjustment(xml_source=adj)
                       for adj in xml.findall("adjustments/adjustment")]
        return Price(due=due, base=base, gst=gst, gst_pc=gst_percent,
                     pst=pst, pst_pc=pst_percent, hst=hst, hst_pc=hst_percent,
                     adjustments=adjustments)
