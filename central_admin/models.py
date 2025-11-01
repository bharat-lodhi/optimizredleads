from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Buyers Leads', 'Buyers Leads'),
        ('Tenant Leads', 'Tenant Leads'),
        ('Study Abroad', 'Study Abroad'),
        ('Online MBA', 'Online MBA'),
        ('Certification', 'Certification'),
        ('Phd/doctorate', 'Phd/doctorate'),
        ('Forex Market', 'Forex Market'),
    ]

    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    heading = models.TextField(blank=True, null=True)
    short_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    features = models.TextField(blank=True, null=True)
    long_description = models.TextField()
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.plan_type}"



# --------------------------Ticket--------------------------------------------------------
