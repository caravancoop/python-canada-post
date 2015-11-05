"""
References module
"""
from lxml import etree
from canada_post.util import InfoObject


class CostCentre(InfoObject):
    """
    Representing a Canada Post Cost centre object
    """
    max_length = 30

    def __init__(self, name):
        self.name = name

    def make_xml(self):
        """
        Insert this cost centre id's XML under the given XML element

        :return: the created <references> lxml.Element object
        """
        assert len(self.name) <= self.max_length, \
                ("Cost centre id can have up to {len} characters".format(
                    len=str(self.max_length)))
        cost_centre = etree.Element('cost-centre')
        cost_centre.text = self.name
        return cost_centre


class References(InfoObject):
    """
    Representing a Canada Post references object containing references the
    user assigns.
    """
    customer_ref_max_length = 35

    def __init__(
            self,
            cost_centre=None,
            customer_ref_1=None,
            customer_ref_2=None,
            **kwargs):
        self.cost_centre = cost_centre
        self.customer_ref_1 = customer_ref_1
        self.customer_ref_2 = customer_ref_2
        super(References, self).__init__(**kwargs)

    def make_xml(self):
        """
        Insert this reference's XML under the given XML element

        :return: the created <references> lxml.Element object
        """
        references = etree.Element('references')

        if self.cost_centre:
            references.append(self.cost_centre.make_xml())

        assert_msg_fmt = 'Customer ref {num} can have up to ' \
                    + str(self.customer_ref_max_length) + ' characters'

        if self.customer_ref_1:
            assert len(self.customer_ref_1) <= self.customer_ref_max_length, \
                assert_msg_fmt.format(num=1)
            ref_1 = etree.Element('customer-ref-1')
            ref_1.text = self.customer_ref_1
            references.append(ref_1)

        if self.customer_ref_2:
            assert len(self.customer_ref_2) <= self.customer_ref_max_length, \
                assert_msg_fmt.format(num=2)
            ref_2 = etree.Element('customer-ref-2')
            ref_2.text = self.customer_ref_2
            references.append(ref_2)

        return references
