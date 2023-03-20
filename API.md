KiKA API
========

API landing page
----------------

https://cdn.kika.de/applikationen/kika-player/app/settings/kikaplayerapp-settings102.json


jq cheat sheet
--------------

JSON keys: `curl {apiUrl} | jq 'to_entries[] | [.key]` or `curl {apiUrl} | jq '_embedded.items[10] | to_entries[] | [.key]`


Pagination
----------

Parameters:
* limit: default 500, e.g. 40
* offset: default 0
* orderBy: appearDate, title
* orderDirection: DESC

Generic pagination response elements:
* `.offset` : current offset
* `.limit` : limit applied to request
* `.total` : total number of elements

Useful resources for paging under API response `._links` like:
```json
{
  "self": {
    "href": "/api/brands?offset=30&limit=10"
  },
  "first": {
    "href": "/api/brands?limit=10"
  },
  "last": {
    "href": "/api/brands?limit=10&offset=230"
  },
  "next": {
    "href": "/api/brands?limit=10&offset=40"
  },
  "previous": {
    "href": "/api/brands?limit=10&offset=20"
  }
}
```

Actual response objects are at `._embedded.items`, depends on API response type


Brands
------

https://www.kika.de/api/v1/kikaplayer/kikaapp/api/brands

Parameters:
* showEmptyBrands : boolean, false

Note that brands seems to be the most reasonable approach to populate the "Shows" (Sendungen) view of the plugin.


Videos
------

https://www.kika.de/api/v1/kikaplayer/kikaapp/api/videos

https://www.kika.de/api/v1/kikaplayer/kikaapp/api/brands/{brandId}/videos

Parameters:
* userAge : max = 13
* geoProtection : name(e.g. 'germany', 'worldwide')
* videoTypes : name(e.g. 'mainContent', 'dgsContent'=Sign language / Gebärdensprche, 'adContent'=Audio description / Hörfassung)
* recursion: boolean

