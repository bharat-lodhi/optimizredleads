from django.shortcuts import render, redirect
from accounts.models import CustomUser

def dashboard(request):
    return render(request, 'central_admin/dashboard.html')

def manage_subadmins(request):
    subs = CustomUser.objects.filter(role='sub_admin')
    return render(request, 'central_admin/manage_subadmins.html', {'subs': subs})

def manage_leads(request):
    return render(request, 'central_admin/manage_leads.html')
