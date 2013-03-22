# Run as a script, this dumps all published places to N3 RDF

from optparse import OptionParser

from rdflib.graph import Graph

from DateTime import DateTime
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer

from pleiades.dump import secure
from pleiades.rdf.common import PlaceGrapher, VocabGrapher

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
    place_grapher = PlaceGrapher(site, request)

    sys.stdout.write("""# Pleiades Places RDF Dump
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
""" % DateTime())

    triple_count = 0
    
    catalog = site['portal_catalog']

    sys.stdout.write("\n# Places\n")

    for b in catalog.searchResults(
            path={'query': "/plone/places"},
            portal_type='Place',
            review_state='published',
            sort_on='getId'):
        obj = b.getObject()
        obj.REQUEST = request.REQUEST
        g = place_grapher.place(obj, vocabs=False)
        #if not g:
        #    import pdb; pdb.set_trace()
        sys.stdout.write(g.serialize(format='turtle'))
        triple_count += len(g)

    sys.stdout.write("\n# Errata\n")
    
    for b in catalog.searchResults(
            path={'query': "/plone/places"},
            portal_type='Link',
            review_state='published',
            sort_on='getId'):
        obj = b.getObject()
        obj.REQUEST = request.REQUEST
        g = place_grapher.place(obj, vocabs=False)
        sys.stdout.write(g.serialize(format='turtle'))
        triple_count += len(g)

    sys.stdout.write("\n# Place and feature types\n")

    v = site['vocabularies']['place-types']
    v.REQUEST = request.REQUEST
    g = VocabGrapher(site, request).scheme(v)
    sys.stdout.write(g.serialize(format='turtle'))
    triple_count += len(g)

    sys.stdout.write("\n# Time periods\n")

    v = site['vocabularies']['time-periods']
    v.REQUEST = request.REQUEST
    g = VocabGrapher(site, request).scheme(v)
    sys.stdout.write(g.serialize(format='turtle'))
    triple_count += len(g)

    sys.stdout.write("\n# Triple count: %d\n" % triple_count)

