# RDF browser views

import logging

from zope.interface import implements, Interface
from zope.publisher.browser import BrowserView

from pleiades.rdf.common import PlaceGrapher, VocabGrapher

EXTS = {'turtle': '.ttl', 'pretty-xml': '.rdf'}

log = logging.getLogger("pleiades.rdf")


class IGraph(Interface):
    def graph():
        """Get a rdflib graph"""


class PlaceGraph(BrowserView):
    implements(IGraph)

    def graph(self):
        return PlaceGrapher(self.context, self.request).place(self.context)


class PlaceGraphTurtle(PlaceGraph):

    def __call__(self):
        self.request.response.setStatus(200)
        self.request.response.setHeader(
            'Content-Type', "text/turtle; charset=utf-8")
        self.request.response.setHeader(
            'Content-Disposition', "filename=%s.ttl" % self.context.getId())
        g = self.graph()
        return g.serialize(format='turtle')


class PlaceGraphRDF(PlaceGraph):

    def __call__(self):
        self.request.response.setStatus(200)
        self.request.response.setHeader(
            'Content-Type', "application/rdf+xml")
        self.request.response.setHeader(
            'Content-Disposition', "filename=%s.rdf" % self.context.getId())
        return self.graph().serialize(format='pretty-xml')


class VocabGraph(BrowserView):
    implements(IGraph)

    def graph(self):
        return VocabGrapher(self.context, self.request).scheme(self.context)


class VocabGraphTurtle(VocabGraph):

    def __call__(self):
        self.request.response.setStatus(200)
        self.request.response.setHeader(
            'Content-Type', "text/turtle; charset=utf-8")
        self.request.response.setHeader(
            'Content-Disposition', "filename=%s.ttl" % self.context.getId())
        g = self.graph()
        return g.serialize(format='turtle')


class VocabGraphRDF(VocabGraph):

    def __call__(self):
        self.request.response.setStatus(200)
        self.request.response.setHeader(
            'Content-Type', "application/rdf+xml")
        self.request.response.setHeader(
            'Content-Disposition', "filename=%s.rdf" % self.context.getId())
        return self.graph().serialize(format='pretty-xml')
