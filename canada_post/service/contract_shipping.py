"""
ContractShipping Canada Post API
https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/shippingmanifest/default.jsf
"""
import logging
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

    def __call__(self, parcel, origin, destination):
        """
        Create a shipping order for the given parcels
        """
        headers = {
            'Accept': "application/vnd.cpc.shipment-v2+xml",
            'Content-type': "application/vnd.cpc.shipment-v2+xml",
            'Accept-language': "en-CA",
        }
        url = self.get_url()
        request=""
        requests.post(url=url, data=request, headers=headers,
                      auth=self.userpass())