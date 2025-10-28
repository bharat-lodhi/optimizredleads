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
    # -----------------------online_mba----------------------------------------
    path('online_mba/', views.online_mba, name='online_mba'),
    path('add_online_mba/', views.add_online_mba, name='add_online_mba'),
    # -----------------------study_abroad----------------------------------------
    path('study_abroad/', views.study_abroad, name='study_abroad'),
    path('add_study_abroad/', views.add_study_abroad, name='add_study_abroad'),
     # Bulk assign URL
    # path('bulk_assign_online_mba/', views.bulk_assign_online_mba, name='bulk_assign_online_mba'),
    
    # ----------------------------User management------------------------------------------
    path('users/', views.users_list, name='users_list'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # --------------------------Leads Upload-------------------------------------------
    # path('upload-leads/<str:category>/', views.upload_leads, name='upload_leads'),
    # path('upload-leads/<str:category>/', views.upload_leads, name='upload_leads'),
    path('upload-leads/<str:category>/', views.upload_leads, name='upload_leads'),

]

