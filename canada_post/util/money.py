from decimal import Decimal
from canada_post.util import InfoObject

ZERO = Decimal("0.00")

def get_decimal(source):
    return Decimal(source or ZERO)

class Adjustment(InfoObject):
    def __init__(self, xml_source=None, **kwargs):
        if xml_source is not None:
            self.code = xml_source.find("adjustment-code").text
            self.name = xml_source.find("adjustment-name").text
            self.cost = get_decimal(xml_source.find("adjustment-cost").text)
            self.percent = xml_source.find("qualifier/percent").text
        super(Adjustment, self).__init__(**kwargs)

    def __repr__(self):
        return "Adjustment(code={code}, name={name}, cost={cost}, " \
               "percent={percent}".format(code=self.code, name=self.name,
                                          cost=self.cost, percent=self.percent)

class Price(InfoObject):
    def __init__(self, due=ZERO, base=ZERO, gst=ZERO, gst_pc=ZERO, pst=ZERO,
                 pst_pc=ZERO, hst=ZERO, hst_pc=ZERO, adjustments=[],
                 **kwargs):

        # due is the total value, will be the sum of everything else, the rest
        #   are the details
        self.due = due

        ### details
        ## base
        self.base = base

        ## taxes
        self.gst = gst
        self.gst_pc = gst_pc
        self.pst = pst
        self.pst_pc = pst_pc
        self.hst = hst
        self.hst_pc = hst_pc
        # tax total
        self.tax_total = gst + pst + hst

        ## adjustment
        self.adjustments=adjustments
        # adjustment total
        self.adjustment_total = sum()

        super(Price, self).__init__(**kwargs)

    def __repr__(self):
        return "Price(due={due}, base={base}, gst={gst}, gst_pc={gst_pc}, " \
               "pst={pst}, pst_pc={pst_pc}, hst={hst}, hst_pc={hst_pc}, " \
               "adjustments={adjustments}".format(due=self.due, base=self.base,
                                                  gst=self.gst,
                                                  gst_pc=self.gst_pc,
                                                  pst=self.pst,
                                                  pst_pc=self.pst_pc,
                                                  hst=self.hst,
                                                  hst_pc=self.hst_pc,
                                                  adjustments=repr(
                                                      self.adjustments))