"""
ContractShipping Canada Post API
https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/shippingmanifest/default.jsf
"""
import logging
from tempfile import NamedTemporaryFile
from lxml import etree
import requests
from canada_post.errors import Wait
from canada_post.service import ServiceBase, CallLinkService
from canada_post.util import InfoObject
import os


def add_child_factory(default_parent):
    def add_child(child_name, parent=default_parent):
        return etree.SubElement(parent, child_name)
    return add_child

class Shipment(InfoObject):
    """
    Shipment class, is the return value of the CreateShipment service.
    It contains
      * tracking pin
      * return tracking pin
      * [shipment ]id
      * [shipment ]status
      * links is a dict of string --> dict where the keys are the rel
         attribute of each link (see the CreateShipment docs in the canadapost
         site. See the CreateShipment docstring for a link) and the keys have an
         'href' which is the link, the same 'rel' value and some other
         attributes, depending on each link
    """
    artifact_type = 'label'
    def __init__(self, xml=None, **kwargs):
        if xml is not None:
            self._from_xml(xml)
        super(Shipment, self).__init__(**kwargs)

    def _from_xml(self, xml):
        # I do this this way because I can't expect all return codes to have all
        #  values, I just fill in every Simple element in self
        for child in xml.getchildren():
            if child.tag == "shipment-id":
                self.id = child.text
            elif child.tag == "shipment-status":
                self.status = child.text
            elif child.tag == "links":
                # I can't make these into InfoObjects because there's a `self`
                #  rel object
                self.links = dict((link['rel'], link)
                    for link in map(lambda l: dict(l.attrib),
                                    child.findall("link")))
            else:
                # expected "tracking-pin" "return-tracking-pin"
                attrname = child.tag.replace("-", "_")
                setattr(self, attrname, child.text)

class Manifest(InfoObject):
    artifact_type = 'artifact'
    def __init__(self, xml=None, **kwargs):
        if xml is not None:
            self._from_xml(xml)
        super(Manifest, self).__init__(**kwargs)

    def _from_xml(self, xml):
        self.po_number = xml.find('po-number').text
        self.links = dict((link['rel'], link) for link in map(lambda l: dict(l.attrib), xml.find('links').findall('link')))

class CreateShipment(ServiceBase):
    """
    CreateShipment Canada Post API (for ContractShipping)
    https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/shippingmanifest/createshipment.jsf
    """
    URL ="https://{server}/rs/{customer}/{mobo}/shipment"
    log = logging.getLogger('canada_post.service.contract_shipping'
                            '.CreateShipment')
    headers = {'Accept': "application/vnd.cpc.shipment-v4+xml",
               'Content-type': "application/vnd.cpc.shipment-v4+xml",
               'Accept-language': "en-CA",
        }

    def __init__(self, auth, url=None):
        if url:
            self.URL = url
        super(CreateShipment, self).__init__(auth)

    def set_link(self, url):
        """
        Sets the link in case you want to set it after initialization
        """
        self.URL = url

    def get_url(self):
        return self.URL.format(server=self.get_server(),
                               customer=self.auth.customer_number,
                               mobo=self.auth.customer_number)

    def _create_address_detail(self, parent, address, add_child):
        """
        Creates the address detail part of the request. You need to do any
        checks outside of this call
        """
        addr_detail = add_child("address-details", parent)
        add_child("address-line-1", addr_detail).text = address.address1
        add_child("address-line-2", addr_detail).text = address.address2
        add_child("city", addr_detail).text = address.city
        if address.province:
            add_child("prov-state", addr_detail).text = address.province
        add_child("country-code", addr_detail).text = address.country_code
        if address.postal_code:
            add_child("postal-zip-code",
                      addr_detail).text = unicode(address.postal_code)
        else:
            assert address.country_code not in ("US", "CA"), (
                u"Addresses within {} require "
                u"a postal code").format(address.country_code)

        return addr_detail

    def __call__(self, parcel, origin, destination, service, group,
                 options=None):
        """
        Create a shipping order for the given parcels

        parcel: must be a canada_post.util.parcel.Parcel
        origin: must be a canada_post.util.address.Origin instance
        destination: must be a canada_post.util.address.Destination instance
        service: must be a canada_post.service.Service instance with at least
            the code parameter set up
        group: must be a string or unicode defining the parcel group that this
            parcel should be added to
        """
        debug = "( DEBUG )" if self.auth.debug else ""
        self.log.info(("Create shipping for parcel %s, from %s to %s{debug}"
                       .format(debug=debug)), parcel, origin, destination)

        # shipment
        shipment = etree.Element(
            "shipment", xmlns="http://www.canadapost.ca/ws/shipment-v4")

        # add child function
        add_child = add_child_factory(shipment)

        add_child("group-id").text = group
        add_child("requested-shipping-point").text = unicode(origin.postal_code)
        delivery_spec = add_child("delivery-spec")
        add_child("service-code", delivery_spec).text = service.code

        # sender
        sender = add_child("sender", delivery_spec)
        if origin.name:
            add_child("name", sender).text = origin.name
        assert origin.company, ("The sender needs a company name for "
                                "Contract Shipping service")
        add_child("company", sender).text = origin.company
        assert origin.phone, ("The sender needs a phone for "
                              "Contact Shipping Service")
        add_child("contact-phone", sender).text = origin.phone

        #destination details, first assertions
        assert any((origin.address1, origin.address2)), (
            "The sender needs an address to Create Shipping")
        assert origin.city, "Need the sender's city to Create Shipping"
        assert origin.province, "Need the sender's province to Create Shipping"
        sender_details = self._create_address_detail(sender, origin, add_child)
        # done sender

        # destination
        dest = add_child("destination", delivery_spec)
        if destination.name:
            add_child("name", dest).text = destination.name
        else:
            # TODO: if the Deliver to Post Office option is used, the name
            #  element must be present for the destination.
            pass
        if destination.company:
            add_child("company", dest).text = destination.company
        if destination.extra:
            add_child("additional-address-info").text = destination.extra
        if destination.phone:
            add_child("client-voice-number", dest).text = destination.phone
        else:
            # Required for destination when service is one of
            #  Expedited Parcel-USA, Xpresspost-USA, Xpresspost-International,
            #  Priority Worldwide Parcel or Pak
            #  (USA.EP, USA.XP, INT.XP, USA.PW.PARCEL, USA.PW.PAK,
            #   INT.PW.PARCEL, INT.PW.PAK)
            if service.code in ("USA.EP", "USA.XP", "INT.XP", "USA.PW.PARCEL",
                                "USA.PW.PAK", "INT.PW.PARCEL", "INT.PK.PAK"):
                assert False, ("Service {code} requires destination to have a "
                               "phone number").format(code=service.code)

        # destination details, first assertions
        assert any((destination.address1, destination.address2)), (
            "Must have address to Create Shipping")
        if not destination.province:
            assert destination.country_code not in ("CA", "US"), (
                "Country code is required for international shippings")
        # and then creation
        dest_details = self._create_address_detail(dest, destination, add_child)
        # done destination

        # customs
        if destination.country_code != 'CA':
            # international shippings require customs details. Several things
            # are hardcoded here, which should be parametrical.
            customs = add_child('customs', delivery_spec)
            # TODO: this should be a parameter
            add_child('currency', customs).text = 'CAD'
            # TODO: this should be a parameter
            # these are the valid options:
            #  GIF = gift
            #  DOC = document
            #  SAM = commercial sample
            #  REP = repair or warranty
            #  SOG = sale of goods
            #  OTH = other
            add_child('reason-for-export', customs).text = 'SOG'
            sku_list = add_child('sku-list', customs)
            assert bool(parcel.items), ("International shipping requires a "
                                        "list of the items")
            for item in parcel.items:
                item_elem = add_child('item', sku_list)
                add_child('customs-number-of-units',
                          item_elem).text = unicode(item.amount)
                add_child('customs-description',
                          item_elem).text = item.description
                add_child('unit-weight', item_elem).text = unicode(item.weight)
                add_child('customs-value-per-unit',
                          item_elem).text = unicode(item.price)

        # done customs

        # options
        if options is not None:
            options_elem = add_child("options", delivery_spec)
            for option in options:
                options_elem.append(option.make_xml())
        # done options

        # parcel
        parcel_chars = add_child("parcel-characteristics", delivery_spec)
        add_child("weight", parcel_chars).text = unicode(parcel.weight)
        if all((parcel.length > 0, parcel.width > 0, parcel.height > 0)):
            dims = add_child("dimensions", parcel_chars)
            add_child("length", dims).text = unicode(parcel.length)
            add_child("width", dims).text = unicode(parcel.width)
            add_child("height", dims).text = unicode(parcel.height)
        add_child("unpackaged", parcel_chars).text = ("true"
                                                      if parcel.unpackaged
                                                      else "false")

        # TODO: notification
        #notification = add_child("notification", delivery_spec)

        print_preferences = add_child("print-preferences", delivery_spec)
        add_child("output-format", print_preferences).text = "4x6"

        # preferences
        preferences = add_child("preferences", delivery_spec)
        add_child("show-packing-instructions", preferences).text = "false"
        # TODO: these two are actually optional (may be "false") for CA
        # shippings
        add_child("show-postage-rate", preferences).text = "false"
        add_child("show-insured-value", preferences).text = "false"

        # settlement-info
        settlement = add_child("settlement-info", delivery_spec)
        # TODO: set paid-by-customer if a different customer is paying for this
        #add_child("paid-by-customer", settlement).text = FOOBAR
        assert self.auth.contract_number, ("Must have a contract number for "
                                           "contract shipping")
        add_child("contract-id", settlement).text = self.auth.contract_number
        # TODO: can be CreditCard as well
        add_child("intended-method-of-payment", settlement).text = "Account"

        url = self.get_url()
        self.log.info("Using url %s", url)
        request = etree.tostring(shipment, pretty_print=self.auth.debug)
        self.log.debug("Request xml: %s", request)
        response = requests.post(url=url, data=request, headers=self.headers,
                                 auth=self.userpass())
        self.log.info("Request returned with status %s", response.status_code)
        self.log.debug("Request returned content: %s", response.content)

        if not response.ok:
            response.raise_for_status()

        # this is a hack to remove the namespace from the response, since this
        #breaks xpath lookup in lxml
        restree = etree.XML(response.content.replace(' xmlns="',
                                                     ' xmlnamespace="'))
        return Shipment(xml=restree)


class GetGroups(ServiceBase):
    URL = "https://{server}/rs/{customer}/{mobo}/group"
    log = logging.getLogger('canada_post.service.contract_shipping'
                            '.GetGroups')
    headers = {'Accept': "application/vnd.cpc.manifest-v4+xml",
               'Accept-language': 'en-CA',
    }

    def get_url(self):
        return self.URL.format(server=self.get_server(),
                               customer=self.auth.customer_number,
                               mobo=self.auth.customer_number)

    def __call__(self, *args, **kwargs):
        self.log.info("Using url %s", url)
        response = requests.post(self.get_url(), headers=self.headers,
                                 auth=self.userpass())

        self.log.info("Request returned with status %s", response.status_code)
        self.log.debug("Request returned content: %s", response.content)
        if not response.ok:
            response.raise_for_status()

        # this is a hack to remove the namespace from the response, since this
        #breaks xpath lookup in lxml
        restree = etree.XML(response.content.replace(' xmlns="',
                                                     ' xmlnamespace="'))
        groups = [group for group in restree.xpath('/groups/group/group-id')]
        return groups


class TransmitShipments(ServiceBase):
    """
    Used to specify shipments to be included in a manifest. Inclusion in a
    manifest is specified by group. Specific shipments may be excluded if
    desired.

    http://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/shippingmanifest/transmitshipments.jsf
    """
    URL ="https://{server}/rs/{customer}/{mobo}/manifest"
    log = logging.getLogger('canada_post.service.contract_shipping'
                            '.TransmitShipments')
    headers = {'Accept': "application/vnd.cpc.manifest+xml",
               'Content-Type': 'application/vnd.cpc.manifest+xml',
               'Accept-language': 'en-CA',
        }

    def get_url(self):
        return self.URL.format(server=self.get_server(),
                               customer=self.auth.customer_number,
                               mobo=self.auth.customer_number)

    def __call__(self, origin, group_ids, name=None, detailed=True,
                 excluded_shipments=[]):
        """
        Transmit shipments to create manifests from

        :origin: a canada_post.util.address.Origin instance
        :group_ids: the list of group ids to be transmitted (string,..32 char)
        :name: the manifest name. Optional. (string ..44 char)
        :detailed: boolean. Define whether a detailed or summarized manifest
            should be rendered. Defaults to True
        :excluded_shipments: an optional list of shipment ids to be excluded
            from the manifest (string ..32 char)
        """

        transmit = etree.Element(
            "transmit-set", xmlns="http://www.canadapost.ca/ws/manifest-v4")
        add_child = add_child_factory(transmit)

        groups = add_child('group-ids')
        for group_id in group_ids:
            add_child('group-id', groups).text = unicode(group_id)

        add_child('requested-shipping-point').text = unicode(origin.postal_code)

        add_child('detailed-manifests').text = 'true' if detailed else 'false'

        # TODO: can be CreditCard as well
        add_child("method-of-payment").text = "Account"

        # address start
        address = add_child('manifest-address')
        add_child('manifest-company', address).text = origin.company
        if name:
            add_child('manifest-name', address).text = name
        add_child('phone-number', address).text = unicode(origin.phone)
        # details start
        details = add_child('address-details', address)
        add_child('address-line-1', details).text = origin.address1
        add_child('address-line-2', details).text = origin.address2
        add_child('city', details).text = origin.city
        add_child('prov-state', details).text = origin.province
        add_child('postal-zip-code', details).text = unicode(origin.postal_code)
        #details end
        # address end

        if excluded_shipments:
            excluded = add_child('excluded-shipments')
            for shipment in excluded_shipments:
                add_child('shipment-id', excluded).text = unicode(shipment)

        url = self.get_url()
        self.log.info("Using url %s", url)
        request = etree.tostring(transmit, pretty_print=self.auth.debug)
        self.log.debug("Request xml: %s", request)

        response = requests.post(url=url, data=request, headers=self.headers,
                                 auth=self.userpass())

        self.log.info("Request returned with status %s", response.status_code)
        self.log.debug("Request returned content: %s", response.content)

        if not response.ok:
            response.raise_for_status()

        # this is a hack to remove the namespace from the response, since this
        #breaks xpath lookup in lxml
        restree = etree.XML(response.content.replace(' xmlns="',
                                                     ' xmlnamespace="'))
        links = [dict(link.attrib) for link in restree.getchildren()]
        return links

class GetManifest(ServiceBase):
    """
    Get a manifest, from a link returned by a previous call to TransmitShipments
    """
    log = logging.getLogger('canada_post.service.contract_shipping'
                            '.GetManifest')
    def __call__(self, link):
        self.log.info("Getting manifest from link %s", link)
        response = requests.get(link['href'], auth=self.userpass())
        self.log.info("Canada Post returned with status code %d",
                      response.status_code)
        self.log.debug("Canada Post returned with content %s", response.content)
        if not response.ok:
            response.raise_for_status()

        restree = etree.XML(response.content.replace(' xmlns="',
                                                     ' xmlnamespace="'))
        return Manifest(xml=restree)

class GetManifestShipments(ServiceBase):
    """
    Get the list of shipment ids for a given manifest
    """
    log = logging.getLogger('canada_post.service.contract_shipping'
                            '.GetManifestShipments')
    def __call__(self, manifest):
        self.log.info("Getting shipments for manifest %s", str(manifest))
        link = manifest.links['manifestShipments']['href']
        self.log.info("Using link %s", link)
        response = requests.get(link, auth=self.userpass())
        self.log.info("Canada Post returned with status code %d",
                      response.status_code)
        self.log.debug("CanadaPost returned with content: %s", response.content)
        if not response.ok:
            response.raise_for_status()

        restree = etree.XML(response.content.replace(' xmlns="',
                                                     ' xmlnamespace="'))
        shipments = []
        for link in restree.findall('link'):
            url = link.attrib['href']
            shipments.append(os.path.basename(url))
        return shipments

class GetArtifact(ServiceBase):
    """
    Download a PDF link from a Shipment or Manifest object, and return a
    temporary file with it
    """
    log = logging.getLogger('canada_post.service.contract_shipping'
                            '.GetArtifact')
    def __call__(self, obj):
        self.log.info("Getting artifact for object %s", str(obj))
        link = obj.links[obj.artifact_type]
        self.log.info("Using link %s", link)
        res = requests.get(link['href'], auth=self.userpass())
        self.log.info("Canada Post returned with status code %d",
                      res.status_code)
        self.log.debug("Canada Post returned with content: %s", res.content)
        if res.status_code == 202:
            raise Wait
        if not res.ok:
            res.raise_for_status()

        img_temp = NamedTemporaryFile(delete=False)
        img_temp.write(res.content)
        img_temp.flush()
        return img_temp

class VoidShipment(CallLinkService):
    """
    Cancel a Contract Shipping created Shipment created by CreateShipment
    """
    log = logging.getLogger("canada_post.service.contract_shipping"
                            ".VoidShipment")
    link_rel = 'self'
    method_name = 'delete'
