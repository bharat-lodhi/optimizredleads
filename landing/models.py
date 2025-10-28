from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('central_admin', 'Central Admin'),
        ('sub_admin', 'Sub Admin'),
        ('subscriber', 'Subscriber'),
    ]

    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='subscriber'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    industry = models.CharField(max_length=50, blank=True, null=True)
    sub_industry = models.CharField(max_length=50, blank=True, null=True)
    preferred_country = models.CharField(max_length=50, blank=True, null=True)

    # Credit / Wallet system
    credit_limit = models.PositiveIntegerField(default=8)  # Default 8 leads for new users
    credits_used = models.PositiveIntegerField(default=0)  # Credits used

    # Plan / Subscription
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='basic'
    )
    plan_start_date = models.DateField(blank=True, null=True)
    plan_end_date = models.DateField(blank=True, null=True)
    plan_status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('expired', 'Expired')],
        default='inactive'
    )

    # Admin / Tracking fields
    is_verified = models.BooleanField(default=False)  # Email/Phone verification
    last_activity = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)  # Admin remarks

    def __str__(self):
        return self.username

    @property
    def available_credits(self):  
        return max(self.credit_limit - self.credits_used, 0)



# from django.conf import settings

# class Payment(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # tumhare custom User model se link
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='payments'
#     )
#     email = models.EmailField(max_length=254, blank=True, null=True)  # guest checkout
#     name = models.CharField(max_length=150, blank=True, null=True)    # guest name

#     razorpay_order_id = models.CharField(max_length=100, unique=True)
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
#     razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
#     amount = models.IntegerField()  # paise me store
#     status = models.CharField(max_length=20, default="created")  # created / paid / failed
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.razorpay_order_id} — {self.user or self.email or 'Anonymous'}"



from django.conf import settings

class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Basic payment fields
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField()  # paise me store
    status = models.CharField(max_length=20, default="created")  # created / paid / failed
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Customer Information
    full_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    company_agency_name = models.CharField(max_length=200, blank=True, null=True)
    business_location_city = models.CharField(max_length=100, blank=True, null=True)
    target_area_location = models.CharField(max_length=200, blank=True, null=True)
    additional_requirements = models.TextField(blank=True, null=True)
    
    # Product Information (optional - agar specific product se link karna ho)
    product_category = models.CharField(max_length=50, blank=True, null=True)
    product_plan_type = models.CharField(max_length=20, blank=True, null=True)
    product_quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.razorpay_order_id} — {self.user or self.full_name or 'Anonymous'}"

    @property
    def amount_in_rupees(self):
        """Convert amount from paise to rupees"""
        return self.amount / 100 if self.amount else 0