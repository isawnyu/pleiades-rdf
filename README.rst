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
* Authors – ``foaf:Person``
* Pleiades Places, Names, Locations – ``pleiades:Place``, ``pleiades:Name``,
  ``pleiades:Location``
* Pleiades vocabulary items – ``skos:Concept``

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

  $ tar tzvf pleiades-latest.tar.gz 
  -rw-r--r-- zope/zope     14291 2013-04-02 18:11:12 authors.ttl
  -rw-r--r-- zope/zope    262883 2013-04-02 18:14:34 errata.ttl
  -rw-r--r-- zope/zope     17048 2013-04-02 18:12:00 place-types.ttl
  -rw-r--r-- zope/zope  14708537 2013-04-02 18:52:35 places-1.ttl
  -rw-r--r-- zope/zope  22835185 2013-04-02 20:28:42 places-2.ttl
  -rw-r--r-- zope/zope  10463935 2013-04-02 21:21:32 places-3.ttl
  -rw-r--r-- zope/zope  15205181 2013-04-02 22:32:57 places-4.ttl
  -rw-r--r-- zope/zope  21944876 2013-04-03 00:36:33 places-5.ttl
  -rw-r--r-- zope/zope  14548858 2013-04-03 02:00:07 places-6.ttl
  -rw-r--r-- zope/zope   9114611 2013-04-03 03:07:33 places-7.ttl
  -rw-r--r-- zope/zope  11176998 2013-04-03 04:12:06 places-8.ttl
  -rw-r--r-- zope/zope   6685326 2013-04-03 04:28:29 places-9.ttl
  -rw-r--r-- zope/zope     50855 2013-04-02 18:11:36 time-periods.ttl

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
``osgeo:AsGeoJSON``, and ``osgeo:AsWKT``. Spatial overlap is expressed using
``osspatial:partiallyOverlaps``.

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

Classical Atlas Project Authors and Contributors
================================================

See the file `pleiades/rdf/cap-authors.csv <pleiades/rdf/cap-authors.csv>`__.

