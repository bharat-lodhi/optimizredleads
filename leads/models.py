from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Base Lead abstract model for common fields
class BaseLead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('converted', 'Converted'),
        ('not_converted', 'Not Converted'),
        ('trashed', 'Trashed'),
    ]

    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(null=True, blank=True)  # new field
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_assigned"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name or "Unnamed Lead"


# Real Estate Lead
class RealEstateLead(BaseLead):
    PROPERTY_TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('land', 'Land'),
        ('other', 'Other'),
    ]
    
    SUB_INDUSTRY_CHOICES = [
        ('Buyers Leads', 'Buyers Leads'),
        ('Tenant Leads', 'Tenant Leads'),
    ]
    
    budget = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    visit_day = models.CharField(max_length=100, null=True, blank=True)  # renamed from interested_to_visit
    requirement_sqft = models.CharField(max_length=100, null=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, null=True, blank=True)
    sub_industry = models.CharField(max_length=20, choices=SUB_INDUSTRY_CHOICES, null=True, blank=True)
    
    
    
# Online MBA Lead
class OnlineMBA(BaseLead):
    course = models.CharField(max_length=255, null=True, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)
    higher_qualification = models.CharField(max_length=255, null=True, blank=True)

# Study Abroad Lead
class StudyAbroad(BaseLead):
    country = models.CharField(max_length=100, null=True, blank=True)
    exam = models.CharField(max_length=100, null=True, blank=True)
    budget = models.CharField(max_length=100, null=True, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)

# Forex Trade Lead - NEW MODEL
class ForexTrade(BaseLead):
    experience = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="How much experience"
    )
    broker = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Initially using broker"
    )
    initial_investment = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Initial investment for trading"
    )
    country = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Forex Trade Lead: {self.full_name or 'Unnamed'}"

# Assignment history log (works for all lead types)
class LeadAssignmentLog(models.Model):
    lead_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    lead_object_id = models.PositiveIntegerField()
    lead = GenericForeignKey('lead_content_type', 'lead_object_id')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lead_assignments"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="lead_assigned_by_admin"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    status_at_assignment = models.CharField(max_length=20, choices=BaseLead.STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        lead_name = str(self.lead) if self.lead else "Lead"
        assignee = str(self.assigned_to) if self.assigned_to else "Unassigned"
        return f"{lead_name} assigned to {assignee}"


# from django.db import models
# from django.conf import settings
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey

# # Base Lead abstract model for common fields
# class BaseLead(models.Model):
#     STATUS_CHOICES = [
#         ('new', 'New'),
#         ('converted', 'Converted'),
#         ('not_converted', 'Not Converted'),
#         ('trashed', 'Trashed'),
#     ]

#     full_name = models.CharField(max_length=255, null=True, blank=True)
#     phone_number = models.CharField(max_length=20, null=True, blank=True)
#     email = models.EmailField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
#     created_at = models.DateTimeField(auto_now_add=True)
#     remark = models.TextField(null=True, blank=True)  # new field
#     assigned_to = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="%(class)s_assigned"
#     )

#     class Meta:
#         abstract = True

#     def __str__(self):
#         return self.full_name or "Unnamed Lead"


# # Real Estate Lead
# class RealEstateLead(BaseLead):
#     PROPERTY_TYPE_CHOICES = [
#         ('residential', 'Residential'),
#         ('commercial', 'Commercial'),
#         ('industrial', 'Industrial'),
#         ('land', 'Land'),
#         ('other', 'Other'),
#     ]
    
#     SUB_INDUSTRY_CHOICES = [
#         ('Buyers Leads', 'Buyers Leads'),
#         ('Tenant Leads', 'Tenant Leads'),
#     ]
    
#     budget = models.CharField(max_length=100, null=True, blank=True)
#     location = models.CharField(max_length=255, null=True, blank=True)
#     visit_day = models.CharField(max_length=100, null=True, blank=True)  # renamed from interested_to_visit
#     requirement_sqft = models.CharField(max_length=100, null=True, blank=True)
#     property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, null=True, blank=True)
#     sub_industry = models.CharField(max_length=20, choices=SUB_INDUSTRY_CHOICES, null=True, blank=True)
    
    
    
# # Online MBA Lead
# class OnlineMBA(BaseLead):
#     course = models.CharField(max_length=255, null=True, blank=True)
#     university = models.CharField(max_length=255, null=True, blank=True)
#     higher_qualification = models.CharField(max_length=255, null=True, blank=True)

# # Study Abroad Lead
# class StudyAbroad(BaseLead):
#     country = models.CharField(max_length=100, null=True, blank=True)
#     exam = models.CharField(max_length=100, null=True, blank=True)
#     budget = models.CharField(max_length=100, null=True, blank=True)
#     university = models.CharField(max_length=255, null=True, blank=True)

# # Assignment history log (works for all lead types)
# class LeadAssignmentLog(models.Model):
#     lead_content_type = models.ForeignKey(
#         ContentType,
#         on_delete=models.CASCADE
#     )
#     lead_object_id = models.PositiveIntegerField()
#     lead = GenericForeignKey('lead_content_type', 'lead_object_id')
#     assigned_to = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="lead_assignments"
#     )
#     assigned_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name="lead_assigned_by_admin"
#     )
#     assigned_at = models.DateTimeField(auto_now_add=True)
#     status_at_assignment = models.CharField(max_length=20, choices=BaseLead.STATUS_CHOICES, default='new')
#     notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         lead_name = str(self.lead) if self.lead else "Lead"
#         assignee = str(self.assigned_to) if self.assigned_to else "Unassigned"
#         return f"{lead_name} assigned to {assignee}"
