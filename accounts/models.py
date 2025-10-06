from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class CustomUser(models.Model):
    ROLE_CHOICES = [
        ('central_admin', 'Central Admin'),
        ('sub_admin', 'Sub Admin'),
        ('subscriber', 'Subscriber'),
    ]
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.email} ({self.role})"
