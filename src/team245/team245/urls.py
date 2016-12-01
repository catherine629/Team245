from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings

import tripPlanner.views

urlpatterns = [
    url(r'^tripPlanner/', include('tripPlanner.urls')),
    url(r'^$', tripPlanner.views.home),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
