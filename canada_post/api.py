"""
Central API module
"""
from canada_post import PROD, Auth
from canada_post.service.rating import (GetRatesClass)

class CanadaPostAPI(object):
    def __init__(self, customer_number, username, password, dev=PROD):
        self.auth = Auth(customer_number, username, password, dev)
        self.get_rates = GetRatesClass(self.auth)
