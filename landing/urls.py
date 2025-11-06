from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'landing'

urlpatterns = [
    # Landing pages
    path('', views.landing, name='landing'),
    path('buyers_leads/', views.buyers_leads, name='buyers_leads'),
    path('tenant_leads/', views.tenant_leads, name='tenant_leads'),
    path('study_abroad/', views.study_abroad, name='study_abroad'),
    path('online_mba/', views.online_mba, name='online_mba'),
    path('certification/', views.certification, name='certification'),
    path('phd_doctorate/', views.phd_doctorate, name='phd_doctorate'),
    path('forex_trader/', views.forex_trader, name='forex_trader'),
    path('about_us/', views.about_us, name='about_us'),
    path('contact_us/', views.contact_us, name='contact_us'),
    
    # User authentication
    path('register/', views.register, name='register'),
    path('start_free_trail/', views.start_free_trail, name='start_free_trail'),
    path('login/', views.login, name='login'),
    
    # Product details
    path('product_details/', views.product_details, name='product_details'),
    
    # ------------------------ Checkout Flow ------------------------
    # Checkout page (show product + GST/fees)
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),

    # Create Razorpay order (AJAX POST)
    path('create_order/<int:product_id>/', views.create_order, name='create_order'),

    # Verify Razorpay payment
    path('checkout/verify_payment/', views.verify_payment, name='verify_payment'),

    # Order success page
    path('checkout/success/', views.order_success, name='order_success'),
    
    
    # ----------------------------------------
    path('terms/', views.terms , name="terms"),
    path('policy/', views.policy , name="policy"),
]

# Serve media files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




