"""
Parcel module
"""

class Parcel(object):
    """
    Represents a Canada Post parcel. Holds things as dimensions, weight,
    tracking number...
    """
    def __init__(self, weight=0, length=0, width=0, height=0, **kwargs):
        """
        weight -- kilograms
        length -- the largest dimension, in cm
        width  -- the second largest dimension in cm
        height -- the smallest dimension in cm
        """
        self.weight = weight
        self.length = length
        self.width = width
        self.height = height
        for k, v in kwargs.items():
            # set any extra kwargs we got
            setattr(self, k, v)
