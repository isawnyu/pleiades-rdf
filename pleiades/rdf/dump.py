# Run as a script, this dumps all published places to N3 RDF

import logging
import sys
from optparse import OptionParser

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from DateTime import DateTime
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.utils import getToolByName
from Testing.makerequest import makerequest

from pleiades.dump import secure, getSite, spoofRequest
from pleiades.rdf.common import PlaceGrapher, PersonsGrapher, VocabGrapher, RegVocabGrapher
from pleiades.rdf.common import place_graph
from pleiades.vocabularies.vocabularies import get_vocabulary

COMMIT_THRESHOLD = 50

if __name__ == '__main__':
    from os import environ

    log = logging.getLogger('pleiades.rdf')

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
        "-e", "--errata", dest="errata",
        default=False,
        help="Dump a erroneous place or multiple erroneous places")
    parser.add_option(
        "-r", "--range", dest="range",
        default=False,
        action='store_true',
        help='Interpret places as a range. Example: "-p=1,3 -r" dumps all places starting with "1" and up to but not including "3" or higher')

    opts, args = parser.parse_args(sys.argv[1:])

    if (int(bool(opts.authors)) + int(bool(opts.vocabulary)) + int(bool(opts.places))) > 1:
        raise ValueError("-a, -p, and -v options are exclusive")

    app = spoofRequest(app)
    server_name = environ.get('SERVER_NAME', 'pleiades.stoa.org').strip()
    vh_root = environ.get('VH_ROOT', '/plone/').strip()
    app.REQUEST.environ.update({'SERVER_PORT': '80', 'REQUEST_METHOD': 'GET',
                                'SERVER_NAME': server_name,
                                'VH_ROOT': vh_root})
    app.REQUEST.setServerURL('http', server_name)
    app.REQUEST.other['VirtualRootPhysicalPath'] = vh_root

    site = getSite(app)
    count = 0

    if opts.authors:

        g = PersonsGrapher(site, app).authors(site)
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

        if opts.vocabulary in ('time-periods', 'place-types'):
            g = RegVocabGrapher(site, app).scheme(opts.vocabulary)
        else:
            vocab = site['vocabularies'][opts.vocabulary]
            g = VocabGrapher(site, app).scheme(vocab)
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

        g = place_graph()
        pids = [s.strip() for s in opts.places.split(",")]
        catalog = site['portal_catalog']
        for b in catalog.searchResults(
                path={'query': "/plone/places"},
                portal_type=['Place', 'Link'],
                review_state='published',
                getId=pids,
                sort_on='getId'):
            obj = b.getObject()
            try:
                if b.portal_type == 'Place':
                    g += PlaceGrapher(site, app).place(obj, vocabs=False)
                elif b.portal_type == 'Link':
                    g += PlaceGrapher(site, app).link(obj)
            except Exception, e:
                log.exception("Failed to add object graph of %r to dump batch: %s", obj, e)
            count += 1
            if count % COMMIT_THRESHOLD == 0:
                transaction.commit()
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

        g = place_graph()
        query = [s.strip() for s in opts.places.split(",")]
        catalog = site['portal_catalog']
        for b in catalog.searchResults(
                path={'query': "/plone/places"},
                portal_type=['Place', 'Link'],
                review_state='published',
                getId={'query': query, 'range': 'min,max'},
                sort_on='getId'):
            obj = b.getObject()
            try:
                if b.portal_type == 'Place':
                    g += PlaceGrapher(site, app).place(obj, vocabs=False)
                elif b.portal_type == 'Link':
                    g += PlaceGrapher(site, app).link(obj)
            except Exception, e:
                log.exception("Failed to add object graph of %r to dump batch: %s", obj, e)
            count += 1
            if count % COMMIT_THRESHOLD == 0:
                transaction.commit()
        sys.stdout.write("""# Pleiades RDF Dump
# Contents: Pleiades Places Range %s
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
# Triple count: %d

""" % (opts.places, DateTime(), len(g)))
        sys.stdout.write(g.serialize(format='turtle'))
        sys.exit(1)

    # Places in /errata
    elif opts.errata and not opts.range:

        g = place_graph()
        pids = [s.strip() for s in opts.errata.split(",")]
        catalog = site['portal_catalog']
        for b in catalog.searchResults(
                path={'query': "/plone/errata"},
                portal_type='Place',
                review_state='published',
                getId=pids,
                sort_on='getId'):
            obj = b.getObject()
            try:
                g += PlaceGrapher(site, app).place(obj, vocabs=False)
            except Exception, e:
                log.exception("Failed to add object graph of %r to dump batch: %s", obj, e)
        sys.stdout.write("""# Pleiades RDF Dump
# Contents: Pleiades Errata %s
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
# Triple count: %d

""" % (opts.places, DateTime(), len(g)))
        sys.stdout.write(g.serialize(format='turtle'))
        sys.exit(1)

    # Places in /errata
    elif opts.errata and opts.range:

        g = place_graph()
        query = [s.strip() for s in opts.errata.split(",")]
        catalog = site['portal_catalog']
        for b in catalog.searchResults(
                path={'query': "/plone/errata"},
                portal_type='Place',
                review_state='published',
                getId={'query': query, 'range': 'min,max'},
                sort_on='getId'):
            obj = b.getObject()
            try:
                g += PlaceGrapher(site, app).place(obj, vocabs=False)
            except Exception, e:
                log.exception("Failed to add object graph of %r to dump batch: %s", obj, e)
        sys.stdout.write("""# Pleiades RDF Dump
# Contents: Pleiades Errata Range %s
# Date: %s
# License: http://creativecommons.org/licenses/by/3.0/us/
# Credits: http://pleiades.stoa.org/credits
# Triple count: %d

""" % (opts.places, DateTime(), len(g)))
        sys.stdout.write(g.serialize(format='turtle'))
        sys.exit(1)

    else:
        raise ValueError("No dump options provided")

