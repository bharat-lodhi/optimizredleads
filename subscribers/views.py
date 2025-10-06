# optimizedleads/subscribers/views.py
from django.shortcuts import render

def dashboard(request):
    return render(request, 'subscribers/dashboard.html')
