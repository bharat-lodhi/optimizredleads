from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Base Lead abstract model for common fields
class BaseLead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_process', 'In Process'),
        ('lead_replacement', 'Lead Replacement'),
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

    # Property to get all status history for this lead
    @property
    def status_history(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return LeadStatusHistory.objects.filter(
            lead_content_type=content_type,
            lead_object_id=self.id
        ).order_by('-created_at')

    # Property to get all remark history for this lead
    @property
    def remark_history(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return LeadRemarkHistory.objects.filter(
            lead_content_type=content_type,
            lead_object_id=self.id
        ).order_by('-created_at')

    # Method to update status with history tracking
    def update_status(self, new_status, user, remark=None):
        content_type = ContentType.objects.get_for_model(self.__class__)
        
        # Create status history
        status_history = LeadStatusHistory.objects.create(
            lead_content_type=content_type,
            lead_object_id=self.id,
            old_status=self.status,
            new_status=new_status,
            changed_by=user
        )
        
        # Update current status
        self.status = new_status
        
        # If remark is provided, create remark history
        if remark:
            remark_history = LeadRemarkHistory.objects.create(
                lead_content_type=content_type,
                lead_object_id=self.id,
                remark_text=remark,
                created_by=user
            )
            # Also update the legacy remark field
            self.remark = remark
        
        self.save()
        return status_history


# Status History Model
class LeadStatusHistory(models.Model):
    lead_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    lead_object_id = models.PositiveIntegerField()
    lead = GenericForeignKey('lead_content_type', 'lead_object_id')
    
    old_status = models.CharField(max_length=20, choices=BaseLead.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=BaseLead.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="status_changes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Lead Status History"

    def __str__(self):
        lead_name = str(self.lead) if self.lead else "Lead"
        return f"Status changed from {self.old_status} to {self.new_status} by {self.changed_by} on {lead_name}"


# Remark History Model
class LeadRemarkHistory(models.Model):
    lead_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    lead_object_id = models.PositiveIntegerField()
    lead = GenericForeignKey('lead_content_type', 'lead_object_id')
    
    remark_text = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lead_remarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Lead Remark History"

    def __str__(self):
        lead_name = str(self.lead) if self.lead else "Lead"
        return f"Remark by {self.created_by} on {lead_name}"


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
    visit_day = models.CharField(max_length=100, null=True, blank=True)
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


# Forex Trade Lead
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

