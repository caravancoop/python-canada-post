"""
Parcel module
"""
from canada_post.util import InfoObject

class Item(InfoObject):
    """
    Represents a single Item in a parcel. It's required for international
    shipments
    """
    def __init__(self, amount, description, weight, price,
                 **kwargs):
        self.amount = amount
        self.description = description
        self.weight = weight
        self.price = price
        super(Item, self).__init__(**kwargs)

class Parcel(InfoObject):
    """
    Represents a Canada Post parcel. Holds things as dimensions, weight,
    tracking number...
    """
    def __init__(self, weight=0, length=0, width=0, height=0, unpackaged=False,
                 items=None,
                 **kwargs):
        """
        weight -- kilograms
        length -- the largest dimension, in cm
        width  -- the second largest dimension in cm
        height -- the smallest dimension in cm
        items  -- a list of Item objects, required only for international
                    shippings
        """
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        self.unpackaged = unpackaged
        self.items = items or []
        super(Parcel, self).__init__(**kwargs)

    def __str__(self):
        return u"Parcel {}kg-{}x{}x{}".format(self.weight,
                                              self.length,
                                              self.width,
                                              self.height)
