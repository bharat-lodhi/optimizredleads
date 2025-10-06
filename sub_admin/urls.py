from django.urls import path
from . import views
app_name = 'sub_admin'

urlpatterns = [
    path('', views.dashboard, name='sub_dashboard'),
    path('leads/', views.manage_leads, name='sub_manage_leads'),
]
