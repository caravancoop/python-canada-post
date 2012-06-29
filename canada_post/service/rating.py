"""
GetRates Canada Post API
https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/rating/default.jsf
"""

class GetRates(object):
    def __call__(self, parcel, origin, destination):
        """
        Call the GetRates service
        """