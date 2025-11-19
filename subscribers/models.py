from django.db import models
from django.contrib.auth import get_user_model

from django.contrib.auth.models import User
import uuid

User = get_user_model()

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('billing', 'Billing & Payment'),
        ('lead', 'Lead Replacement'),
        ('feature', 'Feature Request'),
        ('other', 'Other'),
    ]

    # Ticket details
    ticket_id = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    description = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    # Admin fields
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets'
    )
    admin_notes = models.TextField(blank=True, null=True)
    replacement_leads = models.JSONField(blank=True, null=True) 
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Start ticket numbering from 710
            last_ticket = Ticket.objects.order_by('-id').first()
            if last_ticket and last_ticket.ticket_id:
                try:
                    last_number = int(last_ticket.ticket_id.split('-')[1])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    next_number = 710
            else:
                # No tickets exist yet, start from 710
                next_number = 710
            
            self.ticket_id = f"TKT-{next_number:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ticket_id} - {self.user.username} - {self.get_category_display()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        
        
        


class CalendarEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lead = models.CharField(max_length=100)  # lead_id store karega
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    event_time = models.TimeField()
    google_calendar_event_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.event_date}"
    
    
    
class GoogleCalendarAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credentials = models.TextField(blank=True, null=True)
    is_connected = models.BooleanField(default=False)
    connected_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - Google Calendar"
