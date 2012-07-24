"""
ContractShipping Canada Post API
https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/shippingmanifest/default.jsf
"""
import logging
from lxml import etree
import requests
from canada_post.service import ServiceBase

class CreateShipping(ServiceBase):
    """
    CreateShipping Canada Post API (for ContractShipping)
    https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/shippingmanifest/createshipment.jsf
    """
    URL ="https://{server}/rs/{customer}/{mobo}/shipment"
    log = logging.getLogger('canada_post.service.contract_shipping'
                            '.CreateShipping')
    def __init__(self, auth, url=None):
        if url:
            self.URL = url
        super(CreateShipping, self).__init__(auth)

    def set_link(self, url):
        """
        Sets the link in case you want to set it after initialization
        """
        self.URL = url

    def get_url(self):
        return self.URL.format(server=self.get_sever(),
                               customer=self.auth.customer_number,
                               mobo=self.auth.customer_number)

    def __call__(self, parcel, origin, destination, service, group):
        """
        Create a shipping order for the given parcels

        parcel: must be a canada_post.util.parcel.Parcel
        origin: must be a canada_post.util.address.Origin instance
        destination: must be a canada_post.util.address.Destination instance
        service: must be a canada_post.service.Service instance with at least
            the code parameter set up
        group: must be a string or unicode defining the parcel group that this
            parcel should be added to
        """
        debug = "( DEBUG )" if self.auth.debug else ""
        self.log.info(("Create shipping for parcel %s, from %s to %s{debug}"
                       .format(debug=debug)), parcel, origin, destination)

        # shipment
        shipment = etree.Element(
            "shipment", xmlns="http://www.canadapost.ca/ws/shipment")
        def add_child(child_name, parent=shipment):
            return etree.SubElement(parent, child_name)
        add_child("group-id").text = group
        add_child("requested-shipping-point").text = unicode(origin.postal_code)
        delivery_spec = add_child("delivery-spec")
        add_child("service-code", delivery_spec).text = service.code

        # sender
        sender = add_child("sender", delivery_spec)
        if origin.name:
            add_child("name", sender).text = origin.name
        assert origin.company, ("The sender needs a company name for "
                                "Contract Shipping service")
        add_child("company", sender).text = origin.company
        assert origin.phone, ("The sender needs a phone for "
                              "Contact Shipping Service")
        add_child("contact-phone", sender).text = origin.phone
        sender_details = add_child("address-details", sender)

        # destination
        dest = add_child("destination", delivery_spec)
        if destination.name:
            add_child("name", dest).text = destination.name
        else:
            # TODO: if the Deliver to Post Office option is used, the name
            #  element must be present for the destination.
            pass
        if destination.company:
            add_child("company", dest).text = destination.company
        dest_details = add_child("address-details", dest)

        # options
        options = add_child("options", delivery_spec)

        # parcel
        parcel_chars = add_child("parcel-characteristics", delivery_spec)

        # notification
        notification = add_child("notification", delivery_spec)

        # preferences
        preferences = add_child("preferences", delivery_spec)

        # settlement
        settlement = add_child("settlement-info", delivery_spec)

        headers = {
            'Accept': "application/vnd.cpc.shipment-v2+xml",
            'Content-type': "application/vnd.cpc.shipment-v2+xml",
            'Accept-language': "en-CA",
        }
        url = self.get_url()
        request=""
        requests.post(url=url, data=request, headers=headers,
                      auth=self.userpass())
