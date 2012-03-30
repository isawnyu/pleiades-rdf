# Run as a script, this dumps all published places to N3 RDF

from optparse import OptionParser
import sys

from rdflib import RDF
from rdflib.graph import Graph

from Testing.makerequest import makerequest

from pleiades.dump import secure
from pleiades.rdf.browser import PlaceGraph
from pleiades.rdf.browser import FOAF, GEO, OSGEO, OSSPATIAL, RDFS, SKOS, SPATIAL
from pleiades.rdf.browser import DCTERMS

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        "-u", "--user", dest="user",
        help="Run script as user")
    opts, args = parser.parse_args(sys.argv[1:])
    site = app['plone']
    secure(site, opts.user or 'admin')

    g = Graph()
    g.bind('rdfs', RDFS)
    g.bind('skos', SKOS)
    g.bind('spatial', SPATIAL)
    g.bind('geo', GEO)
    g.bind('foaf', FOAF)
    g.bind('osgeo', OSGEO)
    g.bind('osspatial', OSSPATIAL)
    g.bind('dcterms', DCTERMS)

    catalog = site['portal_catalog']
    for b in catalog.searchResults(
        portal_type='Place',
        review_state='published',
        sort_on='getId'):
        place = b.getObject()
        context = makerequest(place)
        g += PlaceGraph(b.getObject(), context.REQUEST).graph()

    sys.stdout.write(g.serialize(format='turtle'))

