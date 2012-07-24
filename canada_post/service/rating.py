"""
GetRates Canada Post API
https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/rating/default.jsf
"""
import logging
from canada_post.service import ServiceBase
from lxml import etree
import requests
from canada_post import (DEV, PROD)
from canada_post.util.money import (get_decimal, Price, Adjustment)

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

class GetRates(ServiceBase):
    URL = "https://{server}/rs/ship/price",

    log = logging.getLogger('canada_post.service.rating.GetRates')

    def get_url(self):
        return self.URL.format(server=self.get_server())

    def __call__(self, parcel, origin, destination):
        """
        Call the GetRates service
        """
        self.log.info("Getting rates for parcel: %s, from %s to %s", parcel,
                      origin, destination)
        request_tree = etree.Element(
            'mailing-scenario', xmlns="http://www.canadapost.ca/ws/ship/rate")
        def add_child(child_name, parent=request_tree):
            return etree.SubElement(parent, child_name)
        add_child("customer-number").text = unicode(self.auth.customer_number)

        # parcel characteristics
        par_chars = add_child("parcel-characteristics")
        add_child("weight", par_chars).text = unicode(parcel.weight)

        # par_chars/dimensions
        if all((parcel.length > 0, parcel.width > 0, parcel.height > 0)):
            dims = add_child("dimensions", par_chars)
            add_child("length", dims).text = unicode(parcel.length)
            add_child("width", dims).text = unicode(parcel.width)
            add_child("height", dims).text = unicode(parcel.height)

        add_child("origin-postal-code").text = origin.postal_code

        # destination
        dest = add_child("destination")
        if destination.country_code == "CA":
            doms = add_child("domestic", dest)
            add_child("postal-code", doms).text = destination.postal_code
        elif destination.country_code == "US":
            us = add_child("united-states")
            add_child("zip-code", us).text = destination.postal_code
        else:
            # international shipping
            intr = add_child("international", dest)
            add_child("country-code", intr).text = destination.country_code

        # our XML tree is complete. On to the request
        headers = {
            'Accept': "application/vnd.cpc.ship.rate+xml",
            'Content-type': "application/vnd.cpc.ship.rate+xml",
            "Accept-language": "en-CA",
        }

        dev = DEV if self.auth.debug else PROD
        url = self.URLS[dev]
        self.log.info("Using url %s", url)
        request = str(etree.tostring(request_tree, pretty_print=self.auth.debug))
        self.log.debug("Request xml: %s", request)
        response = requests.post(url, data=request, headers=headers,
                                 auth=self.userpass())
        self.log.info("Request returned with status %s", response.status_code)
        self.log.debug("Request returned content: %s", response.content)
        if not response.ok:
            response.raise_for_status()

        # this is a hack to remove the namespace from the response, since this
        #breaks xpath lookup in lxml
        restree = etree.XML(response.content.replace(' xmlns="',
                                                     ' xmlnamespace="'))
        services = [Service(xml_subtree=price)
                    for price in restree.findall("price-quote")]

        return services
