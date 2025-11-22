# optimizedleads/subscribers/urls.py
from django.urls import path
from . import views
app_name = 'subscribers'

urlpatterns = [
    path('', views.dashboard, name='subscribers'),
    # path('my-leads/', views.my_leads, name='my_leads'),
    # path('update_lead_status/', views.update_lead_status, name='update_lead_status'),
    path('my-leads/', views.my_leads, name='my_leads'),
    path('update_lead_status/', views.update_lead_status, name='update_lead_status'),
    path('add_lead_remark/', views.add_lead_remark, name='add_lead_remark'),
    path('get_lead_remarks/', views.get_lead_remarks, name='get_lead_remarks'),
    path('get_lead_status_history/', views.get_lead_status_history, name='get_lead_status_history'),
    # path('replaced-leads/', views.replaced_leads, name='replaced_leads'),
    path('replacement-history/', views.replacement_history_user, name='replacement_history_user'),

    path('submit-ticket/', views.submit_ticket, name='submit_ticket'),
    path('tickets/', views.my_tickets, name='tickets'),
    path('search-leads/', views.search_leads_ajax, name='search_leads'),
    path('celender/', views.celender, name='celender'),
    
    #-----Celender --------------------
    path('create_calendar_event/', views.create_calendar_event, name='create_calendar_event'),
    path('get_calendar_events/', views.get_calendar_events, name='get_calendar_events'),
    
    path('connect-google-calendar/', views.connect_google_calendar, name='connect_google_calendar'),
    path('google-auth-callback/', views.google_auth_callback, name='google_auth_callback'),
]

