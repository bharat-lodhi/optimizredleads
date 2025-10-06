from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.leads_list, name='list'),
    path('add/', views.add_lead, name='add'),
    path('assign/', views.assign_leads, name='assign'),
    path('export/csv/', views.export_leads_csv, name='export_csv'),
    path('export/excel/', views.export_leads_excel, name='export_excel'),
    path('export/pdf/', views.export_leads_pdf, name='export_pdf'),
]
