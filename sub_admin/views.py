from django.shortcuts import render

def dashboard(request):
    return render(request, 'sub_admin/dashboard.html')

def manage_leads(request):
    return render(request, 'sub_admin/manage_leads.html')
