from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse('<h2>OptimizedLeads — Starter</h2><p>Visit /accounts/login/ to login or /accounts/register/ to create user.</p>  <h1><a href="/accounts/register/">Register<a></h1>  <h1><a href="/accounts/login/">Login<a></h1>')

urlpatterns = [
    path('', home),
    path('accounts/', include('accounts.urls')),
    path('central-admin/', include('central_admin.urls', namespace='central_admin')),
    path('sub-admin/', include('sub_admin.urls', namespace='sub_admin')),
    path('leads/', include('leads.urls')),
    path('subscribers/', include('subscribers.urls', namespace='subscribers')),
]