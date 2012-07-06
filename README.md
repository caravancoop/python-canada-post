python-canada-post
==================

This package aims to be a python interface to the Canada Post Developer Program
REST API (via HTTP Post requests with XML data)

It's a W.I.P. and any and all contributions are welcome.

Usage
-----

For now, set up `USERNAME`, `PASSWORD` and `CUSTOMER_NUMBER` in the
`canada_post` package itself, create a `util.parcel.Parcel` with your parcel,
`util.address.Origin` with the origin's `postal_code` (with no spaces) as a
and constructor's keyword argument (e.g.: orig = Origin(postal_code="A0A101"))
a `util.address.Destination` with the destination's `country_code` and
`postal code`, and use them to call `canada_post.service.rating.GetRates`

The utility classes don't do almost anything so far, but are mostly a glorified
dict, but behavior will probably grow into them as the library grows.