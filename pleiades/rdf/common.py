# Common classes and functions

import csv
import os
import re
from urlparse import urlparse

import geojson
import logging
from pleiades import capgrids
from rdflib import BNode, Literal, Namespace, RDF, URIRef
from rdflib.graph import Graph
from shapely.geometry import asShape, box
from shapely import wkt

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from pleiades.geographer.geo import location_precision
from pleiades.json.browser import wrap
from pleiades.vocabularies.vocabularies import get_vocabulary

from Products.PleiadesEntity.browser.attestations import TimeSpanWrapper

CITO_URI = "http://purl.org/spar/cito/"
CITO = Namespace(CITO_URI)

DCTERMS_URI = "http://purl.org/dc/terms/"
DCTERMS = Namespace(DCTERMS_URI)

FOAF_URI = "http://xmlns.com/foaf/0.1/"
FOAF = Namespace(FOAF_URI)

GEO_URI = "http://www.w3.org/2003/01/geo/wgs84_pos#"
GEO = Namespace(GEO_URI)

OSGEO_URI = "http://data.ordnancesurvey.co.uk/ontology/geometry/"
OSGEO = Namespace(OSGEO_URI)

SKOS_URI = "http://www.w3.org/2004/02/skos/core#"
SKOS = Namespace(SKOS_URI)

RDFS_URI = "http://www.w3.org/2000/01/rdf-schema#"
RDFS = Namespace(RDFS_URI)

SPATIAL_URI = "http://geovocab.org/spatial#"
SPATIAL = Namespace(SPATIAL_URI)

OSSPATIAL_URI = "http://data.ordnancesurvey.co.uk/ontology/spatialrelations/"
OSSPATIAL = Namespace(OSSPATIAL_URI)

OWL_URI = "http://www.w3.org/2002/07/owl#"
OWL = Namespace(OWL_URI)

PLACES = "http://pleiades.stoa.org/places/"

PLEIADES_URI = "http://pleiades.stoa.org/places/vocab#"
PLEIADES = Namespace(PLEIADES_URI)

PROVO_URI = "http://www.w3.org/TR/prov-o/#"
PROV = Namespace(PROVO_URI)

log = logging.getLogger('pleiades.rdf')

def geoContext(place):
    note = place.getModernLocation() or ""
    if not note:
        descr = place.Description() or ""
        match = re.search(r"cited: BAtlas (\d+) (\w+)", descr)
        if match:
            note = "Barrington Atlas grid %s %s" % (
                match.group(1), match.group(2).capitalize())
    note = unicode(note, "utf-8")
    note = unicode(note.replace(unichr(174), unichr(0x2194)))
    note = note.replace(unichr(0x2192), unichr(0x2194))
    return note

def bind_all(g):
    g.bind('cito', CITO)
    g.bind('dcterms', DCTERMS)
    g.bind('owl', OWL)
    g.bind('foaf', FOAF)
    g.bind('geo', GEO)
    g.bind('osgeo', OSGEO)
    g.bind('osspatial', OSSPATIAL)
    g.bind('owl', OWL)
    g.bind('pleiades', PLEIADES)
    g.bind('prov', PROV)
    g.bind('rdfs', RDFS)
    g.bind('skos', SKOS)
    g.bind('spatial', SPATIAL)
    return g

def place_graph():
    g = bind_all(Graph())
    return g

def skos_graph():
    g = Graph()
    g.bind('dcterms', DCTERMS)
    g.bind('foaf', FOAF)
    g.bind('skos', SKOS)
    g.bind('owl', OWL)
    return g


def user_info(context, username):
    mtool = getToolByName(context, 'portal_membership')
    if username == 'T. Elliott': un = 'thomase'
    elif username == 'S. Gillies': un = 'sgillies'
    else: un = username
    member = mtool.getMemberById(un)
    if member:
        return {
            "id": member.getId(),
            "fullname": member.getProperty('fullname'),
            'url': "http://pleiades.stoa.org/author/" + member.getId()}
    else:
        return {"id": None, "fullname": un, 'url': None}

def principals(context):
    creators =  getattr(context, 'Creators', [])
    if callable(creators):
        creators = list(creators())
    creators = [p.strip() for r in creators for p in r.split(',')]
    contributors = list(context.Contributors())
    contributors = [p.strip() for r in contributors for p in r.split(',')]
    if ("sgillies" in creators and
            ("sgillies" in contributors or "S. Gillies" in contributors)):
        creators.remove("sgillies")
    return creators, contributors

authority = {}
f = open(os.path.join(os.path.dirname(__file__), 'authority.csv'))
reader = csv.reader(f)
for label, username, uri in list(reader)[1:]:
    authority[label] = (username, uri)
f.close()

class PleiadesGrapher(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog = getToolByName(context, 'portal_catalog')
        self.wftool = getToolByName(context, 'portal_workflow')
        self.portal = getToolByName(context, 'portal_url').getPortalObject()
        self.vocabs = self.portal['vocabularies']
        self.authority = authority

    def dcterms(self, context, g):
        """Return a set of tuples covering DC metadata"""

        curl = context.absolute_url()
        vh_root = context.REQUEST.environ.get('VH_ROOT')
        if vh_root:
            curl = curl.replace(vh_root, '')
        subj = URIRef(curl)

        # Title, Description, and Modification Date
        g.add((
            subj,
            DCTERMS['title'],
            Literal(context.Title())))
        g.add((
            subj,
            DCTERMS['description'],
            Literal(context.Description())))
        g.add((
            subj,
            DCTERMS['modified'],
            Literal(context.ModificationDate())))

        # Tags
        for tag in context.Subject():
            g.add((
                subj,
                DCTERMS['subject'],
                Literal(tag)))

        # Authors
        creators, contributors = principals(context)

        for principal in creators:
            p = user_info(context, principal)
            url = p.get('url')
            if not url:
                if principal in self.authority:
                    username, url = self.authority.get(principal)
                    if username and not url:
                        url = "http://pleiades.stoa.org/author/" + username
            if url:
                pnode = URIRef(url)
            else:
                pnode = BNode()
            g.add((subj, DCTERMS['creator'], pnode))
            if not url and p.get('fullname'):
                g.add((pnode, RDF.type, FOAF['Person']))
                g.add((pnode, FOAF['name'], Literal(p.get('fullname'))))

        for principal in contributors:
            p = user_info(context, principal)
            url = p.get('url')
            if not url:
                if principal in self.authority:
                    username, url = self.authority.get(principal)
                    if username and not url:
                        url = "http://pleiades.stoa.org/author/" + username
            if url:
                pnode = URIRef(url)
            else:
                pnode = BNode()
            g.add((subj, DCTERMS['contributor'], pnode))
            if not url and p.get('fullname'):
                g.add((pnode, RDF.type, FOAF['Person']))
                g.add((pnode, FOAF['name'], Literal(p.get('fullname'))))

        return g


class PlaceGrapher(PleiadesGrapher):

    def link(self, context):
        g = place_graph()

        purl = context.absolute_url()
        vh_root = context.REQUEST.environ.get('VH_ROOT')
        if vh_root:
            purl = purl.replace(vh_root, '')
        context_page = purl
        context_subj = URIRef(context_page + "#this")

        remote = context.getRemoteUrl()
        if remote:
            uri = "/".join([
                "http:/",
                urlparse(context_page)[1],
                remote.strip("/")])
            g.add((context_subj, OWL['sameAs'], URIRef(uri + "#this")))

        return g

    def temporal(self, context, g, subj, vocabs=True):

        periods = get_vocabulary('time_periods')
        periods = dict([(p['id'], p) for p in periods])
        purl = self.portal.absolute_url() + '/vocabularies/time-periods'
        vh_root = context.REQUEST.environ.get('VH_ROOT')
        if vh_root:
            purl = purl.replace(vh_root, '')

        for attestation in context.getAttestations():
            g.add((
                subj,
                PLEIADES['during'],
                URIRef(purl + "/" +
                    attestation['timePeriod'])))
            if vocabs:
                g = RegVocabGrapher(self.portal, self.request).concept(
                    periods[attestation['timePeriod']], g)

        span = TimeSpanWrapper(context).timeSpan
        if span:
            g.add((
                subj,
                PLEIADES['start_date'],
                Literal(span['start'])))
            g.add((
                subj,
                PLEIADES['end_date'],
                Literal(span['end'])))

        return g

    def provenance(self, context, g, subj):
        pnode = BNode()
        g.add((subj, PROV['wasDerivedFrom'], pnode))
        g.add((pnode, RDFS['label'], Literal(context.getInitialProvenance())))
        return g

    def references(self, context, g, subj):
        mapping = {
            'seeAlso': 'citesAsRelated', 'seeFurther': 'citesForInformation'}
        # seeAlso
        for c in context.getReferenceCitations():
            identifier = c.get('identifier')
            citation_type = c.get('type')
            citation_range = c.get('range')
            if (identifier and
                    identifier.startswith("http://") or
                    identifier.startswith("doi") or
                    identifier.startswith("issn") or
                    identifier.startswith("ibsn")):
                ref =  URIRef(c.get('identifier').strip())
            else:
                ref = BNode()
            g.add((
                subj,
                CITO[mapping.get(citation_type, citation_type)],
                ref))
            g.add((
                subj,
                DCTERMS['bibliographicCitation'],
                Literal(citation_range)))

        return g

    def place(self, context, vocabs=True):
        """Create a graph centered on a Place and its Feature."""
        g = place_graph()

        purl = context.absolute_url()
        vh_root = context.REQUEST.environ.get('VH_ROOT')
        if vh_root:
            purl = purl.replace(vh_root, '')

        context_page = purl
        context_subj = URIRef(context_page)
        feature_subj = URIRef(context_page + "#this")

        # Type
        g.add((context_subj, RDF.type, PLEIADES['Place']))

        g.add((context_subj, RDF.type, SKOS['Concept']))
        g.add((
            context_subj,
            SKOS['inScheme'],
            URIRef("http://pleiades.stoa.org/places")))

        # Triples concerning the real world ancient place.
        g.add((feature_subj, RDF.type, SPATIAL['Feature']))

        # primary topic
        g.add((
            feature_subj,
            FOAF['primaryTopicOf'],
            context_subj))

        # title as rdfs:label
        g.add((
            feature_subj,
            RDFS['label'],
            Literal(context.Title())))

        # description as rdfs:comment
        g.add((
            feature_subj,
            RDFS['comment'],
            Literal(context.Description())))

        g = self.dcterms(context, g)
        g = self.provenance(context, g, context_subj)

        # Place or feature types

        place_types = self.vocabs['place-types']
        pcats = set(filter(None, context.getPlaceType()))
        for pcat in pcats:
            item = place_types.get(pcat)
            if not item:
                continue
            iurl = item.absolute_url()
            vh_root = item.REQUEST.environ.get('VH_ROOT')
            if vh_root:
                iurl = iurl.replace(vh_root, '')
            g.add((
                context_subj,
                PLEIADES['hasFeatureType'],
                URIRef(iurl)))

            if vocabs:
                g = VocabGrapher(place_types, self.request).concept(
                    place_types[pcat], g)

        # Names as skos:label and prefLabel
        folder_path = "/".join(context.getPhysicalPath())
        brains = self.catalog(
            path={'query': folder_path, 'depth': 1},
            portal_type='Name',
            review_state='published')
        names = [b.getObject() for b in brains]

        for obj in names:
            name = Literal(
                obj.getNameAttested() or obj.getNameTransliterated(),
                obj.getNameLanguage() or None)
            g.add((
                context_subj,
                SKOS['altLabel'],
                name))

            name_subj = URIRef(context_page + "/" + obj.getId())
            g.add((context_subj, PLEIADES['hasName'], name_subj))
            g.add((name_subj, RDF.type, PLEIADES['Name']))

            g = self.dcterms(obj, g)

            g = self.temporal(obj, g, name_subj, vocabs=vocabs)
            g = self.provenance(obj, g, name_subj)
            g = self.references(obj, g, name_subj)

            nameAttested = obj.getNameAttested()
            if nameAttested:
                g.add((
                    name_subj,
                    PLEIADES['nameAttested'],
                    Literal(nameAttested, obj.getNameLanguage() or None)))

            for nr in obj.getNameTransliterated().split(','):
                nr = nr.strip()
                g.add((name_subj, PLEIADES['nameRomanized'], Literal(nr)))

        # representative point
        xs = []
        ys = []
        folder_path = "/".join(context.getPhysicalPath())
        brains = self.catalog(
            path={'query': folder_path, 'depth': 1},
            portal_type='Location',
            review_state='published')
        locs = [b.getObject() for b in brains]
        features = [wrap(ob, 0) for ob in locs]

        # get representative point
        loc_prec = location_precision(context)
        if loc_prec == 'precise':
            repr_point = None
            for f in features:
                if f.geometry and hasattr(f.geometry, '__geo_interface__'):
                    shape = asShape(f.geometry)
                    b = shape.bounds
                    xs.extend([b[0], b[2]])
                    ys.extend([b[1], b[3]])
                    if repr_point is None:
                        repr_point = shape.centroid
            if len(xs) * len(ys) > 0:
                bbox = [min(xs), min(ys), max(xs), max(ys)]
            else:
                bbox = None

            if repr_point:
                g.add((
                    context_subj,
                    GEO['lat'],
                    Literal(repr_point.y)))
                g.add((
                    context_subj,
                    GEO['long'],
                    Literal(repr_point.x)))
            elif bbox:
                g.add((
                    context_subj,
                    GEO['lat'],
                    Literal((bbox[1]+bbox[3])/2.0)))
                g.add((
                    context_subj,
                    GEO['long'],
                    Literal((bbox[0]+bbox[2])/2.0)))
        elif loc_prec == 'rough':
            for loc in locs:
                ref = loc.getLocation()
                gridbase = "http://atlantides.org/capgrids/"
                if ref and ref.startswith(gridbase):
                    params = ref.rstrip("/")[len(gridbase):].split("/")
                    if len(params) == 1:
                        mapnum = params[0]
                        grids = [None]
                    elif len(params) == 2:
                        mapnum = params[0]
                        grids = [v.upper() for v in params[1].split("+")]
                    else:
                        log.error("Invalid location identifier %s" % ref)
                        continue
                    for grid in grids:
                        grid_uri = gridbase + mapnum + "#" + (grid or "this")
                        bounds = capgrids.box(mapnum, grid)
                        shape = box(*bounds)

                        g.add((
                            context_subj,
                            OSSPATIAL['within'],
                            URIRef(grid_uri)))

                        e = URIRef(grid_uri + "-extent")  # the grid's extent
                        g.add((e, RDF.type, OSGEO['AbstractGeometry']))
                        g.add((
                            URIRef(grid_uri),
                            OSGEO['extent'],
                            e))
                        g.add((
                            e,
                            OSGEO['asGeoJSON'],
                            Literal(geojson.dumps(shape))))
                        g.add((
                            e,
                            OSGEO['asWKT'],
                            Literal(wkt.dumps(shape))))

        # Locations
        for obj in locs:

            locn_subj = URIRef(context_page + "/" + obj.getId())
            g.add((context_subj, PLEIADES['hasLocation'], locn_subj))
            g.add((locn_subj, RDF.type, PLEIADES['Location']))

            g = self.dcterms(obj, g)

            g = self.temporal(obj, g, locn_subj, vocabs=vocabs)
            g = self.provenance(obj, g, locn_subj)
            g = self.references(obj, g, locn_subj)

            dc_locn = obj.getLocation()
            gridbase = "http://atlantides.org/capgrids/"

            if dc_locn and dc_locn.startswith(gridbase):
                try:
                    params = dc_locn.rstrip("/")[len(gridbase):].split("/")
                    if len(params) == 1:
                        mapnum = params[0]
                        grids = [None]
                    elif len(params) == 2:
                        mapnum = params[0]
                        grids = [v.upper() for v in params[1].split("+")]
                    elif len(params) >= 3:
                        mapnum = params[0]
                        grids = [v.upper() for v in params[1:]]
                    else:
                        log.error("Invalid location identifier %s" % ref)
                        continue

                    for grid in grids:
                        grid_uri = gridbase + mapnum + "#" + (grid or "this")
                        bounds = capgrids.box(mapnum, grid)
                        shape = box(*bounds)

                        g.add((
                            locn_subj,
                            OSSPATIAL['partiallyOverlaps'],
                            URIRef(grid_uri)))

                        e = URIRef(grid_uri + "-extent") # the grid's extent
                        g.add((e, RDF.type, OSGEO['AbstractGeometry']))
                        g.add((
                            URIRef(grid_uri),
                            OSGEO['extent'],
                            e))
                        g.add((
                            e,
                            OSGEO['asGeoJSON'],
                            Literal(geojson.dumps(shape))))
                        g.add((
                            e,
                            OSGEO['asWKT'],
                            Literal(wkt.dumps(shape))))

                except:
                    log.exception("Exception caught computing grid extent for %r", obj)

            else:
                try:
                    f = wrap(obj, 0)
                    if (f.geometry and
                            hasattr(f.geometry, '__geo_interface__')):
                        shape = asShape(f.geometry)
                        g.add((
                            locn_subj,
                            OSGEO['asGeoJSON'],
                            Literal(geojson.dumps(shape))))
                        g.add((
                            locn_subj,
                            OSGEO['asWKT'],
                            Literal(wkt.dumps(shape))))
                except:
                    log.exception("Couldn't wrap and graph %r", obj)

        # connects with
        for f in (context.getConnections() +
                  context.getConnections_from()):
            if self.wftool.getInfoFor(f, 'review_state') != 'published':
                continue
            furl = f.absolute_url()
            vh_root = context.REQUEST.environ.get('VH_ROOT')
            if vh_root:
                furl = furl.replace(vh_root, '')
            feature_obj = URIRef(furl + "#this")
            g.add((feature_subj, SPATIAL['C'], feature_obj))
            g.add((context_subj, RDFS['seeAlso'], URIRef(furl)))

        # dcterms:coverage
        coverage = geoContext(context)
        if coverage:
            g.add((
                context_subj,
                DCTERMS['coverage'],
                Literal(coverage) ))

        g = self.references(context, g, context_subj)

        return g


class VocabGrapher(PleiadesGrapher):

    def concept(self, term, g):
        """Return a set of tuples representing the term"""

        turl = term.absolute_url()
        vh_root = term.REQUEST.environ.get('VH_ROOT')
        if vh_root:
            turl = turl.replace(vh_root, '')
        term_ref = URIRef(turl)
        label = term.getTermValue()
        note = term.Description()

        g.add((
            term_ref,
            RDF.type,
            SKOS['Concept']))
        g.add((
            term_ref,
            SKOS['prefLabel'],
            Literal(label, "en")))

        if note:
            g.add((
                term_ref,
                SKOS['scopeNote'],
                Literal(note, "en")))

        vocab = aq_parent(aq_inner(term))
        vurl = vocab.absolute_url()
        vh_root = vocab.REQUEST.environ.get('VH_ROOT')
        if vh_root:
            vurl = vurl.replace(vh_root, '')
        g.add((
            term_ref,
            SKOS['inScheme'],
            URIRef(vurl)))

        return g

    def scheme(self, vocab):
        g = place_graph()
        vurl = vocab.absolute_url()
        vh_root = vocab.REQUEST.environ.get('VH_ROOT')
        if vh_root:
            vurl = vurl.replace(vh_root, '')
        g.add((
            URIRef(vurl),
            RDF.type,
            SKOS['ConceptScheme']))

        g = self.dcterms(vocab, g)

        for key, term in vocab.items():
            g = self.concept(term, g)

        return g


class RegVocabGrapher(PleiadesGrapher):

    def concept(self, term, g):
        """Return a set of tuples representing the term"""

        vurl = self.portal.absolute_url() + '/vocabularies/time-periods'
        turl = vurl + '/' + term['id']
        vh_root = self.request.environ.get('VH_ROOT')
        if vh_root:
            turl = turl.replace(vh_root, '')
        term_ref = URIRef(turl)
        label = term['title']
        note = term['description']
        same_as = term['same_as']

        g.add((
            term_ref,
            RDF.type,
            SKOS['Concept']))
        g.add((
            term_ref,
            SKOS['prefLabel'],
            Literal(label, "en")))

        if note:
            g.add((
                term_ref,
                SKOS['scopeNote'],
                Literal(note, "en")))

        if same_as:
            g.add((
                term_ref,
                OWL['sameAs'],
                URIRef(same_as)))

        vh_root = self.request.environ.get('VH_ROOT')
        if vh_root:
            vurl = vurl.replace(vh_root, '')
        g.add((
            term_ref,
            SKOS['inScheme'],
            URIRef(vurl)))

        return g

    def scheme(self, vocab_name):
        g = place_graph()
        vurl = self.portal.absolute_url() + '/vocabularies/%s' % vocab_name
        vh_root = self.request.environ.get('VH_ROOT')
        if vh_root:
            vurl = vurl.replace(vh_root, '')
        g.add((
            URIRef(vurl),
            RDF.type,
            SKOS['ConceptScheme']))

        # No dublin core in registry vocabs
        # hardcoding for now
        g.add((
            URIRef(vurl),
            DCTERMS['title'],
            Literal("Time Periods")))
        g.add((
            URIRef(vurl),
            DCTERMS['description'],
            Literal("Named time periods for the site.")))

        vocab = get_vocabulary(vocab_name)
        for term in vocab:
            g = self.concept(term, g)

        return g


class PersonsGrapher(PleiadesGrapher):

    def authors(self, context):
        # Note: Authors without Pleiades pages will appear as blank nodes
        # in the Places RDF files.

        g = place_graph()
        fake_users = ['auser', 'juser']
        contributors = set(self.catalog.uniqueValuesFor('Contributors'))
        creators = set(self.catalog.uniqueValuesFor('Creator'))
        users = contributors.union(creators)
        for u in fake_users:
            if u in users:
                users.remove(u)

        # First, the Pleiades site contributors.
        for u in users:

            info = user_info(context, u)
            fullname = info.get('fullname')

            # Site users.
            if info.get('url') and fullname:
                subj = URIRef(info['url'])
                g.add((subj, RDF.type, FOAF['Person']))
                g.add((subj, FOAF['name'], Literal(fullname)))

                if fullname in self.authority:
                    username, uri = self.authority[fullname]
                    g.add((subj, OWL['sameAs'], URIRef(uri)))

            # Non-user authors listed in the authority file.
            elif u in self.authority:
                username, uri = self.authority[u]
                if username and not uri:
                    uri = "http://pleiades.stoa.org/author/" + username
                if not uri:
                    continue
                subj = URIRef(uri)
                g.add((subj, RDF.type, FOAF['Person']))
                g.add((subj, FOAF['name'], Literal(label)))

        return g

