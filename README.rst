============
Pleiades RDF
============

This is the pleiades.rdf package. It provides RDF views of individual Pleiades
places (such as http://pleiades.stoa.org/places/1043/turtle) and the
comprehensive RDF dataset dumps at
http://atlantides.org/downloads/pleiades/rdf/ and CKAN's Data Hub.

Vocabularies
============

Pleiades uses terms from several different vocabularies and ontologies.

Citation Ontology
-----------------

`<http://purl.org/spar/cito/>`__

The terms ``cito:cites``, ``cito:citesAsRelated``, ``cito:citesForEvidence``, and
``cito:citesForInformation`` are used to identify works cited and their
context.

Dublin Core
-----------

`<http://purl.org/dc/terms/>`__

Every content item in Pleiades has a ``dc:title``, ``dc:description``,
``dc:creator``, and one or more ``dc:contributor``.

FOAF
----

`<http://xmlns.com/foaf/0.1/>`__

All content creators and contributors are ``foaf:Person``.

GeoVocab
--------

`<http://geovocab.org/spatial#>`__

Geographic connections are expressed using ``spatial:C``.

Ordnance Survey Ontology
------------------------

`<http://data.ordnancesurvey.co.uk/ontology/geometry/>`__

`<http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>`__

The extents of spatial objects are expressed using ``osgeo:AbstractGeometry``,
``osgeo:AsGeoJSON``, and ``osgeo:AsWKT``. Spatial containment is expressed
using ``osspatial:within``.

OWL
---

`<http://www.w3.org/2002/07/owl#>`__

The ``owl:sameAs`` property is used to identify the resolved duplicates within
Pleiades.

Pleiades
--------

`<http://pleiades.stoa.org/places/vocab#>`__

The Pleiades RDF vocabulary consists of 3 classes: ``pleiades:Place``,
``pleiades:Location``, and ``pleiades:Name``.

Instances of ``pleiades:Place`` identify their component Names and Locations
with ``pleiades:hasName`` and ``pleiades:hasLocation``.

All Names and Locations identify time periods during which they were in use
with ``pleiades:during``. The minimum attested year of the oldest and the
maximum attested year of the most recent of these time periods are also
provided using ``pleiades:start_date`` and ``pleiades:end_date``.

Locations identify associated feature types with ``pleiades:hasFeatureType``.

The attested form of a name in its original writing system is bound to the
``pleiades:nameAttested`` property, while its romanizations are bound to
``pleiades:nameRomanized``.

SKOS Core
---------

`<http://www.w3.org/2004/02/skos/core#>`__

SKOS terms are used to describe the feature type and time period vocabularies
of Pleiades.

RDF Schema
----------

`<http://www.w3.org/2000/01/rdf-schema#>`__

We try to give every thing in our graph a ``rdfs:label``. Things of the ancient
world – as opposed to their counterparts in the Pleiades site – have
a ``rdfs:comment`` instead of ``dc:description``. Pleiades also uses
``rdfs:seeAlso`` for links to Wikipedia, etc.

W3C Geographic Position
-----------------------

`<http://www.w3.org/2003/01/geo/wgs84_pos#>`__

This is probably the most well known vocabulary for geographic location. The terms
``geo:lat`` and ``geo:long`` are used to help spatially naive systems get
a grip on Pleiades data.

W3C Provenance
--------------

`<http://www.w3.org/TR/prov-o/#>`__

The sources of all Pleiades content are identified using
``prov:wasDerivedFrom``.

