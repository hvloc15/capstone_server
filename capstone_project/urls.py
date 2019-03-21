from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from swagger.swagger import schema_view

urlpatterns = [
    url(r'^docs/$', schema_view),
    url(r'^api/', include("api.urls"))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
