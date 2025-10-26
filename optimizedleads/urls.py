from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('', include('landing.urls')),
    path('central-admin/', include('central_admin.urls', namespace='central_admin')),
    path('sub-admin/', include('sub_admin.urls', namespace='sub_admin')),
    path('leads/', include('leads.urls', namespace='leads')),  # Add namespace here
    path('subscribers/', include('subscribers.urls', namespace='subscribers')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)