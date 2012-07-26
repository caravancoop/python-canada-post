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