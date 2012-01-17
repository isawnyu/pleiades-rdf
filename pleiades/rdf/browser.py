# RDF browser views

import logging
import geojson
from rdflib import Literal, Namespace, RDF, URIRef
from rdflib.graph import Graph
from shapely.geometry import asShape, box
from shapely import wkt

from zope.interface import implements, Interface
from zope.publisher.browser import BrowserView

from Products.CMFCore.utils import getToolByName

from pleiades.geographer.geo import IGeoreferenced, location_precision
from pleiades.json.browser import wrap
from pleiades import capgrids

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

PLACES = "http://pleiades.stoa.org/places/"

EXTS = {'turtle': '.ttl', 'pretty-xml': '.rdf'}

log = logging.getLogger("pleiades.rdf")

class IGraph(Interface):
    def graph():
        """Get a rdflib graph"""

class PlaceGraph(BrowserView):
    implements(IGraph)

    def graph(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        wftool = getToolByName(self.context, 'portal_workflow')

        g = Graph()
        g.bind('rdfs', RDFS)
        g.bind('skos', SKOS)
        g.bind('spatial', SPATIAL)
        g.bind('geo', GEO)
        g.bind('foaf', FOAF)
        g.bind('osgeo', OSGEO)
        g.bind('osspatial', OSSPATIAL)

        context_page = PLACES + self.context.getId()
        context_subj = URIRef(context_page + "#this")
        
        # Type
        g.add((context_subj, RDF.type, SPATIAL['Feature']))

        # primary topic
        g.add((
            context_subj,
            FOAF['primaryTopicOf'],
            URIRef(context_page)))

        # title as rdfs:label
        g.add((
            context_subj,
            RDFS['label'], 
            Literal(self.context.Title())))

        # description as rdfs:comment
        g.add((
            context_subj,
            RDFS['comment'], 
            Literal(self.context.Description())))

        # Names as skos:label and prefLabel
        folder_path = "/".join(self.context.getPhysicalPath())
        brains = catalog(
            path={'query': folder_path, 'depth': 1}, 
            portal_type='Name', 
            review_state='published')
        objs = [b.getObject() for b in brains]
        name_ratings = [
            catalog.getIndexDataForRID(
                b.getRID())['average_rating'] for b in brains]
        rated_names = sorted(
            zip(name_ratings, objs),
            reverse=True)
        
        for rating, obj in rated_names[:1]:
            name = Literal(
                obj.getNameAttested() or obj.getNameTransliterated(),
                obj.getNameLanguage() or None)
            if rating and rating[0] > 0.0:
                g.add((
                    context_subj,
                    SKOS['prefLabel'],
                    name))
            else:
                g.add((
                    context_subj,
                    SKOS['altLabel'],
                    name))
        
        for rating, obj in rated_names[1:]:
            name = Literal(
                obj.getNameAttested() or obj.getNameTransliterated(),
                obj.getNameLanguage() or None)
            g.add((
                context_subj,
                SKOS['altLabel'], 
                name))
        
        ## representative point
        xs = []
        ys = []
        folder_path = "/".join(self.context.getPhysicalPath())
        brains = catalog(
            path={'query': folder_path, 'depth': 1}, 
            portal_type='Location', 
            review_state='published')
        locs = [b.getObject() for b in brains]
        location_ratings = [
            catalog.getIndexDataForRID(
                b.getRID())['average_rating'] for b in brains]
        features = [wrap(ob, 0) for ob in locs]

        # get representative point
        loc_prec = location_precision(self.context)
        if loc_prec == 'precise':
            repr_point = None
            for r, f in sorted(zip(location_ratings, features), reverse=True):
                if f.geometry and hasattr(f.geometry, '__geo_interface__'):
                    shape = asShape(f.geometry)
                    b = shape.bounds
                    xs.extend([b[0], b[2]])
                    ys.extend([b[1], b[3]])
                    if repr_point is None and r and r[0] > 0.0:
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

        # connects with
        for f in (
            self.context.getConnections() + self.context.getConnections_from()):
            if wftool.getInfoFor(f, 'review_state') != 'published':
                continue
            feature_obj = URIRef(PLACES + f.getId() + "#this")
            g.add((context_subj, SPATIAL['C'], feature_obj))

        # seeAlso
        for c in self.context.getReferenceCitations():
            identifier = c.get('identifier')
            if identifier and identifier.startswith("http://"):
                g.add((
                    context_subj, 
                    RDFS['seeAlso'], 
                    URIRef(c.get('identifier').strip()) ))

        return g

class PlaceGraphTurtle(PlaceGraph):

    def __call__(self):
        self.request.response.setStatus(200)
        self.request.response.setHeader(
            'Content-Type', "text/turtle; charset=utf-8")
        self.request.response.setHeader(
            'Content-Disposition', "filename=%s.ttl" % self.context.getId())
        return self.graph().serialize(format='turtle')

class PlaceGraphRDF(PlaceGraph):

    def __call__(self):
        self.request.response.setStatus(200)
        self.request.response.setHeader(
            'Content-Type', "application/rdf+xml")
        self.request.response.setHeader(
            'Content-Disposition', "filename=%s.rdf" % self.context.getId())
        return self.graph().serialize(format='pretty-xml')

