============
Pleiades RDF
============

This is the pleiades.rdf package. It provides RDF views of individual Pleiades
places (such as http://pleiades.stoa.org/places/1043/turtle) and the
comprehensive RDF dataset dumps at
http://atlantides.org/downloads/pleiades/rdf/.

RDF Views of Places
===================

The RDF views of Places (such as http://pleiades.stoa.org/places/1043/turtle
for Turtle or http://pleiades.stoa.org/places/1043/rdf for RDF/XML) contain
triples with the following classes of subjects:

* Ancient World Places (real past world entities)
* Authors (real world people)
* Pleiades Places, Names, Locations (web resources)
* Pleiades vocabulary items (web resources)

Generally, every thing in the graph has at least a label, but detailed data is
provided only for the Place at the center of the graph and its Locations and
Names. The vocabularies used to express the detailed data are enumerated below.

RDF Dataset Dumps
=================

The pleiades-latest.tar.gz archive contains 9 files of RDF for Places
(places-[1-9].ttl), one file of RDF about erroneous Places (errata.ttl), a file
describing Pleiades authors (authors.ttl), and two vocabularies
(place-types.ttl and time-periods.ttl).

.. sourcecode:: console

  # tar tzf pleiades-latest.tar.gz 
  authors.ttl
  errata.ttl
  place-types.ttl
  places-1.ttl
  places-2.ttl
  places-3.ttl
  places-4.ttl
  places-5.ttl
  places-6.ttl
  places-7.ttl
  places-8.ttl
  places-9.ttl
  time-periods.ttl

These archives are created weekly. The difference between these files and the
single Place graphs is that authors and vocabularies are represented separately
and not duplicated within the batches of Places.

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

