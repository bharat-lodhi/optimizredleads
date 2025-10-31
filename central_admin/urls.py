from django.urls import path
from . import views

app_name = 'central_admin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('analytics/', views.analytics, name='analytics'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/', views.categories, name='categories'),
    #-------------------------Products---------------------------------------------
    path('add_product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='products_list'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    # -----------------------real_estate-----------------------------------------
    path('real_estate/', views.real_estate, name='real_estate'),
    path('add_real_estate/', views.add_real_estate, name='add_real_estate'),
    path('edit_real_estate/<int:lead_id>/', views.edit_real_estate, name='edit_real_estate'),
    path('delete_real_estate/<int:lead_id>/', views.delete_real_estate, name='delete_real_estate'),
    # -----------------------online_mba----------------------------------------
    path('online_mba/', views.online_mba, name='online_mba'),
    path('add_online_mba/', views.add_online_mba, name='add_online_mba'),
    path('edit_online_mba/<int:lead_id>/', views.edit_online_mba, name='edit_online_mba'),
    path('delete_online_mba/<int:lead_id>/', views.delete_online_mba, name='delete_online_mba'),

    # -----------------------study_abroad----------------------------------------
    path('study_abroad/', views.study_abroad, name='study_abroad'),
    path('add_study_abroad/', views.add_study_abroad, name='add_study_abroad'),
    path('edit_study_abroad/<int:lead_id>/', views.edit_study_abroad, name='edit_study_abroad'),
    path('delete_study_abroad/<int:lead_id>/', views.delete_study_abroad, name='delete_study_abroad'),
    # -------------------------Forex-trade---------------------------------------------------
    path('add_forex_trade/', views.add_forex_trade, name='add_forex_trade'),
    path('forex_trade/', views.forex_trade, name='forex_trade'), 
    path('edit_forex_trade/<int:lead_id>/', views.edit_forex_trade, name='edit_forex_trade'),
    path('delete_forex_trade/<int:lead_id>/', views.delete_forex_trade, name='delete_forex_trade'),
    # ----------------------------User management------------------------------------------
    path('users/', views.users_list, name='users_list'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # --------------------------Leads Upload-------------------------------------------
    # path('upload-leads/<str:category>/', views.upload_leads, name='upload_leads'),
    # path('upload-leads/<str:category>/', views.upload_leads, name='upload_leads'),
    path('upload-leads/<str:category>/', views.upload_leads, name='upload_leads'),
    path('contact-leads/', views.contact_leads_list, name='contact_leads_list'),

]

