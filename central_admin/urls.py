from django.urls import path
from . import views

app_name = 'central_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('subadmins/', views.manage_subadmins, name='manage_subadmins'),
    path('leads/', views.manage_leads, name='manage_leads'),
]
