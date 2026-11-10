from django.urls    import path
from .              import endpoints

urlpatterns = [
    path('v1/snapshot', endpoints.Snapshot.as_view(), name='mobile-snapshot-api'),
]
