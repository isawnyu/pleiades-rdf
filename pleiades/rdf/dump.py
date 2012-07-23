# Run as a script, this dumps all published places to N3 RDF

from optparse import OptionParser

from rdflib.graph import Graph

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer

from pleiades.dump import secure
from pleiades.rdf.common import PlaceGrapher, place_graph, skos_graph

if __name__ == '__main__':
    from os import environ
    from sys import argv, stdin, stdout

    def makerequest(app, stdout=stdout):
        resp = HTTPResponse(stdout=stdout)
        if "SERVER_NAME" not in environ:
            environ['SERVER_NAME']='foo'
        environ['SERVER_PORT']='80'
        environ['REQUEST_METHOD'] = 'GET'
        req = HTTPRequest(stdin, environ, resp)
        if 'VH_ROOT' in environ:
            req.REQUEST['VH_ROOT'] = environ['VH_ROOT']
        return app.__of__(RequestContainer(REQUEST = req))

    parser = OptionParser()
    parser.add_option(
        "-u", "--user", dest="user",
        help="Run script as user")
    opts, args = parser.parse_args(argv[1:])

    site = app['plone']
    secure(site, opts.user or 'admin')
    request = makerequest(site)
    grapher = PlaceGrapher(site, request)
    places = place_graph()
    skos = skos_graph()

    catalog = site['portal_catalog']
    for b in catalog.searchResults(
            path={'query': "/plone/places"},
            portal_type='Place',
            review_state='published',
            sort_on='getId'):
        obj = b.getObject()
        obj.REQUEST = request.REQUEST
        places += grapher.place(obj)
        skos += grapher.skos(obj)

    places += skos

    # Finally, the resolved duplicates
    dupes = place_graph()
    for b in catalog.searchResults(
            path={'query': "/plone/places"},
            portal_type='Link',
            review_state='published',
            sort_on='getId'):
        obj = b.getObject()
        obj.REQUEST = request.REQUEST
        dupes += grapher.link(obj)

    places += dupes
    sys.stdout.write(places.serialize(format='turtle'))

