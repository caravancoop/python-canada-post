"""
Different Canada Post Developer Program services
"""
import logging
from canada_post import DEV, PROD
from canada_post.util.money import Price, get_decimal, Adjustment
import requests

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

    def get_url(self):
        raise NotImplementedError

    def userpass(self):
        return self.auth.username, self.auth.password

class CallLinkService(ServiceBase):
    """
    Services that are called from link details returned by a prior call

    override klass.method to change GET to POST, DELETE, PUT, etcetera
    """
    log = logging.getLogger('canada_post.service.CallLinkService')
    link_rel = 'BAD_NAME'
    method_name = 'get'
    def __init__(self, *args, **kwargs):
        super(CallLinkService, self).__init__(*args, **kwargs)
        self.method = getattr(requests, self.method_name)
    def __call__(self, shipment):
        """
        Void the Shipment object passed as parameter, using it's 'void' link
        """
        self.log.info("Calling %s on shipment %s", self.__class__.__name__,
                      shipment)
        link = shipment.links[self.link_rel]
        url = link['href']
        self.log.info("Calling url %s", url)
        headers = {
            'Accept': link['media-type'],
            'Accept-language': 'en-CA',
            }
        res = self.method(url, headers=headers, auth=(self.userpass()))
        self.log.info("Response status code: %d", res.status_code)
        if not res.ok:
            res.raise_for_status()
        return True

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
            self.transit_time = data.get('transit_time', -1)

    def __repr__(self):
        return (u"Service(data={{ code='{code}', link='{link}', name='{name}', "
               u"price={price} }})").format(code=self.code,
                                            link=repr(self.link),
                                            name=self.name,
                                            price=repr(self.price))

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
        self.transit_time = xml.find("service-standard/expected-transit-time")
        if self.transit_time is not None:
            self.transit_time = int(self.transit_time.text)

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
