"""
GetRates Canada Post API
https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/rating/default.jsf
"""
from lxml import etree
import requests
from canada_post import (DEV, PROD, CUSTOMER_NUMBER)

class GetRates(object):
    URLS = {
        DEV: "https://ct.soa-gw.canadapost.ca/rs/ship/price",
        PROD: "https://soa-gw.canadapost.ca/rs/ship/price",
    }

    @classmethod
    def __call__(cls, parcel, origin, destination):
        """
        Call the GetRates service
        """
        request_tree = etree.Element(
            'mailing-scenario', xmlns="http://www.canadapost.ca/ws/ship/rate")
        def add_child(child_name, parent=request_tree):
            return etree.SubElement(request_tree, child_name)
        add_child("customer-number").text = CUSTOMER_NUMBER

        # parcel characteristics
        par_chars = add_child("parcel-characteristics")
        add_child("weight", par_chars).text = parcel.weight

        # par_chars/dimensions
        dims = add_child("dimensions", par_chars)
        add_child("lenght", dims).text = parcel.length
        add_child("width", dims).text = parcel.width
        add_child("height", dims).text = parcel.height

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
            'Content-Type': "application/vnd.cpc.ship.rate+xml",
            "Accept-language": "en-CA",
        }

        response = requests