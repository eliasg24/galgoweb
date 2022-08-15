# Django
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

from django.conf import settings
from django.views.static import serve

urlpatterns = [
    
    path('admin/', admin.site.urls),

    path("", include(("dashboards.urls", "dashboards"), namespace="dashboards")),
    
    path("", include(("calendario.urls", "calendario"), namespace="calendario")),
    
    path("", include(("utilidades.urls", "utilidades"), namespace="utilidades")),
    
    path("", include(("galgoapi.urls", "galgoapi"), namespace="galgoapi")),
    
    path("", include(("aetoappapi.urls", "aetoappapi"), namespace="aetoappapi")),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT})
]