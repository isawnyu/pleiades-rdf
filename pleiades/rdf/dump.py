# Run as a script, this dumps all published places to N3 RDF

from optparse import OptionParser

from rdflib.graph import Graph

from DateTime import DateTime
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer

from pleiades.dump import secure
from pleiades.rdf.common import PlaceGrapher, PersonsGrapher, VocabGrapher

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
    parser.add_option(
        "-a", "--authors", dest="authors",
        default=False,
        action="store_true",
        help="Dump authors")
    parser.add_option(
        "-v", "--vocabulary", dest="vocabulary",
        default=None,
        help="Dump a named vocabulary")
    parser.add_option(
        "-p", "--places", dest="places",
        default=False,
        help="Dump a place or multiple places")
    parser.add_option(
        "-r", "--range", dest="range",
        default=False,
        action='store_true',
        help='Interpret places as a range. Example: "-p=1,3 -r" dumps all places starting with "1" and up to but not including "3" or higher')

    opts, args = parser.parse_args(argv[1:])

    if (int(bool(opts.authors)) + int(bool(opts.vocabulary)) + int(bool(opts.places))) > 1:
        raise ValueError("-a, -p, and -v options are exclusive")

    site = app['plone']
    secure(site, opts.user or 'admin')
    request = makerequest(site)
    site.REQUEST = request.REQUEST

    if opts.authors:

        g = PersonsGrapher(site, request).authors(site)
        sys.stdout.write("""# Pleiades RDF Dump
# Contents: Pleiades Authors
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
# Triple count: %d

""" % (DateTime(), len(g)))
        sys.stdout.write(g.serialize(format='turtle'))
        sys.exit(1)

    elif opts.vocabulary:

        vocab = site['vocabularies'][opts.vocabulary]
        g = VocabGrapher(site, request).scheme(vocab)
        sys.stdout.write("""# Pleiades RDF Dump
# Contents: Pleiades Vocabulary '%s'
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
# Triple count: %d

""" % (opts.vocabulary, DateTime(), len(g)))
        sys.stdout.write(g.serialize(format='turtle'))
        sys.exit(1)

    elif opts.places and not opts.range:

        g = None
        pids = [s.strip() for s in opts.places.split(",")]
        catalog = site['portal_catalog']
        for b in catalog.searchResults(
                path={'query': "/plone/places"},
                portal_type='Place',
                review_state='published',
                getId=pids,
                sort_on='getId'):
            obj = b.getObject()
            obj.REQUEST = request.REQUEST
            if not g:
                g = PlaceGrapher(site, request).place(obj, vocabs=False)
            else:
                g += PlaceGrapher(site, request).place(obj, vocabs=False)
        sys.stdout.write("""# Pleiades RDF Dump
# Contents: Pleiades Places %s
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
# Triple count: %d

""" % (opts.places, DateTime(), len(g)))
        sys.stdout.write(g.serialize(format='turtle'))
        sys.exit(1)

    elif opts.places and opts.range:

        g = None
        query = [s.strip() for s in opts.places.split(",")]
        catalog = site['portal_catalog']
        for b in catalog.searchResults(
                path={'query': "/plone/places"},
                portal_type='Place',
                review_state='published',
                getId={'query': query, 'range': 'min,max'},
                sort_on='getId'):
            obj = b.getObject()
            obj.REQUEST = request.REQUEST
            if not g:
                g = PlaceGrapher(site, request).place(obj, vocabs=False)
            else:
                g += PlaceGrapher(site, request).place(obj, vocabs=False)
        sys.stdout.write("""# Pleiades RDF Dump
# Contents: Pleiades Places Range %s
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
# Triple count: %d

""" % (opts.places, DateTime(), len(g)))
        sys.stdout.write(g.serialize(format='turtle'))
        sys.exit(1)

    else:
        raise ValueError("No dump options provided")

