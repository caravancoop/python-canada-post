"""
Central API module
"""
from canada_post import PROD, Auth
from canada_post.service.contract_shipping import (CreateShipment, VoidShipment,
                                                   TransmitShipments)
from canada_post.service.rating import (GetRates)

class CanadaPostAPI(object):
    def __init__(self, customer_number, username, password, contract_number="",
                 dev=PROD):
        self.auth = Auth(customer_number, username, password, contract_number,
                         dev)
        self.get_rates = GetRates(self.auth)
        self.create_shipment = CreateShipment(self.auth)
        self.void_shipment = VoidShipment(self.auth)
        self.transmit_shipments = TransmitShipments(self.auth)
