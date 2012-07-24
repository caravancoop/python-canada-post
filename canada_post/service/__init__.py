"""
Different Canada Post Developer Program services
"""
from canada_post import DEV, PROD

class ServiceBase(object):
    """
    base class for API endpoints/services
    """
    SERVER = {
        DEV: "ct.soa-gw.canadapost.ca",
        PROD: "ct.soa-gw.canadapost.ca",
    }

    def __init__(self, auth):
        self.auth = auth

    def get_sever(self):
        return self.SERVER[self.auth.dev]

    def userpass(self):
        return self.auth.username, self.auth.password
