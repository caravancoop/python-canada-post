python-canada-post
==================

This package aims to be a python interface to the Canada Post Developer Program
REST API (via HTTP Post requests with XML data)

It's a W.I.P. and any and all contributions are welcome.

Usage
-----

Example usage

    from canada_post import api, DEV, PROD
    from canada_post.util.parcel import Parcel
    from canada_post.util.address import Origin, Destination
    cpa = api.CanadaPostAPI(customer_number, api_username, api_password,
                            contract_number, dev=DEV if DEBUG else PROD)
    parcel = Parcel(weight=2, length=100, width=60, height=30)
    origin = address.Origin(province=myprovince, address=myaddress, phone=myphone,
                            city=mycity,  postal_code=myposcode, company=company_name)
    dest =  address.Destination(country_code=dest_code, postal_code=dest_pc, province=dest_prov,
                                city=dest_city, address=dest_address)
    services = cpa.get_rates(parcel, origin, dest)
    # this returns a list of Service objects, with a bunch of data, say you select the one you want
    #  from the list somehow
    service = select_service(services)
    # group_name is a string, it creates a shipment group, the whole group gets sent together,
    #  so if you need to send a bunch of parcels together, pass the same string as the group param
    shipment = cpa.create_shipment(parcel, origin, dest, service, group_name)
    print shipment.id, shipment.status, shipment.tracking_pin
    print shipment.links['label']

Plese notice that the API is less than stable yet (for example, the
`create_shipment` interface that's been implemented is just for the Contract
Shipment service, so it should probably be under a sublayer something like
`cpa.contract.create_shipment`).

The links object is a dict of

    rel -> { 'href':...,
             'index':...,
             'rel':...,
             'media-type':...
           }

(it could be different depending on the rel, see the response part of
https://www.canadapost.ca/cpo/mc/business/productsservices/developers/services/shippingmanifest/createshipment.jsf
for details). A better solution for this might be created in the near future,
I'll try to be very clear about any changes.

Changelog
=========
0.0.3-2: Changed name from create_shipping to create_shipment