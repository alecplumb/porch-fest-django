import hashlib

from django.http                    import HttpResponse, HttpResponseNotModified
from django.utils.http              import parse_etags, quote_etag
from rest_framework.permissions     import AllowAny
from rest_framework.renderers       import JSONRenderer
from rest_framework.views           import APIView

from performers.models              import Genre, Performer
from porches.models                 import Performance, Porch
from .serializers                   import (
    GenreSerializer,
    PerformanceSerializer,
    PerformerSerializer,
    PorchSerializer,
)

# Bump when the response shape changes in a way old app versions can't read.
SCHEMA_VERSION = 1


class Snapshot(APIView):
    """
    Everything the mobile apps need to browse the festival offline, in one
    response: genres, performers, porches and performances.

    Only approved porches that have coordinates are included, along with the
    performances at those porches and the performers who play them.

    The response carries an ETag derived from its content. Clients send it back
    as If-None-Match and get an empty 304 when nothing has changed.
    """
    authentication_classes  = []
    permission_classes      = [AllowAny]

    def get(self, request):
        body = JSONRenderer().render(self.build(request))
        etag = quote_etag(hashlib.sha256(body).hexdigest())

        # Compare weakly: proxies (nginx gzip) may rewrite "abc" as W/"abc".
        sent = [tag.removeprefix("W/") for tag in parse_etags(request.headers.get("If-None-Match", ""))]
        if etag in sent or "*" in sent:
            response = HttpResponseNotModified()
        else:
            response = HttpResponse(body, content_type="application/json")
        response["ETag"]            = etag
        response["Cache-Control"]   = "no-cache"
        return response

    def build(self, request):
        context = {"request": request}

        porches = (
            Porch.objects
            .filter(approved=True, coordinates__isnull=False)
            .select_related("sponsor")
            .order_by("number", "name", "id")
        )
        performances = (
            Performance.objects
            .filter(porch__approved=True, porch__coordinates__isnull=False)
            .order_by("start_time", "id")
        )
        performers = (
            Performer.objects
            .filter(performances__in=performances)
            .distinct()
            .prefetch_related("genres")
            .order_by("name", "id")
        )
        genres = Genre.objects.order_by("name", "id")

        return {
            "schema_version":   SCHEMA_VERSION,
            "genres":           GenreSerializer(genres, many=True).data,
            "performers":       PerformerSerializer(performers, many=True, context=context).data,
            "porches":          PorchSerializer(porches, many=True, context=context).data,
            "performances":     PerformanceSerializer(performances, many=True).data,
        }
