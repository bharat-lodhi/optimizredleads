# optimizedleads/subscribers/urls.py
from django.urls import path
from . import views
app_name = 'subscribers'

urlpatterns = [
    path('', views.dashboard, name='subscribers'),
    path('my-leads/', views.my_leads, name='my_leads'),
    path('tickets/', views.support_tickets, name='tickets'),
    path('update_lead_status/', views.update_lead_status, name='update_lead_status'),

]
