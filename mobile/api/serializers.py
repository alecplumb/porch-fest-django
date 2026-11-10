from rest_framework     import serializers
from performers.models  import Genre, Performer
from porches.models     import Performance, Porch

# Serializers for the mobile snapshot. Every field is listed explicitly so
# private data (owner and performer contact details) can never leak by default.


def absolute_media_url(serializer, image):
    if not image:
        return None
    request = serializer.context.get("request")
    return request.build_absolute_uri(image.url) if request else image.url


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Genre
        fields  = ("id", "name", "slug")


class PerformerSerializer(serializers.ModelSerializer):
    genre_ids   = serializers.SerializerMethodField()
    image_url   = serializers.SerializerMethodField()

    class Meta:
        model   = Performer
        fields  = ("id", "slug", "name", "bio", "link", "genre_ids", "image_url")

    def get_genre_ids(self, obj):
        # Uses the prefetched genres; sorted so the payload (and its ETag) is stable.
        return sorted(genre.id for genre in obj.genres.all())

    def get_image_url(self, obj):
        return absolute_media_url(self, obj.profile_picture)


class PorchSerializer(serializers.ModelSerializer):
    lat         = serializers.SerializerMethodField()
    lng         = serializers.SerializerMethodField()
    image_url   = serializers.SerializerMethodField()
    sponsor     = serializers.SerializerMethodField()

    class Meta:
        model   = Porch
        fields  = (
            "id",
            "slug",
            "name",
            "number",
            "description",
            "street_address",
            "city",
            "lat",
            "lng",
            "image_url",
            "sponsor",
            "sponsored",
            "vendor",
            "childrens_activities",
            "after_party",
            "parking",
            "info_booth",
            "porta_potty",
            "drinking_water",
            "bicycle_repair",
        )

    def get_lat(self, obj):
        return obj.coordinates.y

    def get_lng(self, obj):
        return obj.coordinates.x

    def get_image_url(self, obj):
        return absolute_media_url(self, obj.porch_picture)

    def get_sponsor(self, obj):
        sponsor = getattr(obj, "sponsor", None)
        if sponsor is None or not sponsor.is_active:
            return None
        return {
            "name":     sponsor.name,
            "level":    sponsor.level,
            "website":  sponsor.website,
            "logo_url": absolute_media_url(self, sponsor.logo),
        }


class PerformanceSerializer(serializers.ModelSerializer):
    porch_id        = serializers.UUIDField()
    performer_id    = serializers.UUIDField()

    class Meta:
        model   = Performance
        fields  = ("id", "porch_id", "performer_id", "start_time", "end_time")
