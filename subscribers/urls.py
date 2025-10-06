# optimizedleads/subscribers/urls.py
from django.urls import path
from . import views
app_name = 'subscribers'

urlpatterns = [
    path('', views.dashboard, name='subscribers_dashboard'),
]
