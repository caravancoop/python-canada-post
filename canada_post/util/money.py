from decimal import Decimal
from canada_post.util import InfoObject

ZERO = Decimal("0.00")

def get_decimal(source):
    return Decimal(source or ZERO)

class Adjustment(InfoObject):
    def __init__(self, xml_source=None, **kwargs):
        if xml_source:
            self.code = xml_source.find("adjustment-code").text
            self.name = xml_source.find("adjustment-name").text
            self.cost = get_decimal(xml_source.find("adjustment-cost").text)
            self.percent = xml_source.find("qualifier/percent").text

        super(Adjustment, self).__init__(**kwargs)

class Price(InfoObject):
    def __init__(self, due=ZERO, base=ZERO, gst=ZERO, gst_pc=ZERO, pst=ZERO,
                 pst_pc=ZERO, hst=ZERO, hst_pc=ZERO, adjustments=[],
                 **kwargs):

        # due is the total value, will be the sum of everything else, the rest
        #   are the details
        self.due = due

        # details
        self.base = base
        self.gst = gst
        self.gst_pc = gst_pc
        self.pst = pst
        self.pst_pc = pst_pc
        self.hst = hst
        self.hst_pc = hst_pc
        self.adjustments=adjustments
        super(Price, self).__init__(**kwargs)
