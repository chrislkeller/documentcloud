# Django
from django.http.response import Http404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Standard Library
from urllib.parse import urlsplit

# DocumentCloud
from documentcloud.oembed.registry import registry


class OEmbedView(APIView):
    """oEmbed endpoint"""

    permission_classes = (AllowAny,)

    def get(self, request):

        if "url" not in request.GET:
            return Response(
                {"error": "url required"}, status=status.HTTP_400_BAD_REQUEST
            )

        def get_int(key):
            """Get the GET parameter as an integer, or return None
            if not present or not a valid integer
            """
            try:
                return int(request.GET[key])
            except (ValueError, KeyError):
                return None

        try:
            query = urlsplit(request.GET["url"]).query
        except ValueError:
            raise Http404

        for oembed in registry:
            for pattern in oembed.patterns:
                match = pattern.match(request.GET["url"])
                if match:
                    oembed_response = oembed.response(
                        request,
                        query,
                        max_width=get_int("max_width"),
                        max_height=get_int("max_height"),
                        **match.groupdict()
                    )
                    return Response(oembed_response)

        raise Http404