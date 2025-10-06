from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('accounts:register')
        user = CustomUser(name=name, email=email, role=role)
        user.set_password(password)
        user.save()
        messages.success(request, 'Registered successfully. Please login')
        return redirect('accounts:login')
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        try:
            user = CustomUser.objects.get(email=email, role=role)
            if user.check_password(password):
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                if user.role == 'central_admin':
                    return redirect('central_admin:dashboard')
                if user.role == 'sub_admin':
                    return redirect('sub_admin:sub_dashboard')
                return redirect('subscribers:subscribers_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found')
    return render(request, 'accounts/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('accounts:login')