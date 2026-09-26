from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def admin_login_required(view_func):
    """Decorator to check if user is admin/staff"""
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='admin_panel:login'  # <-- FIXED
    )(view_func)

def admin_login(request):
    """Admin login page - separate from user login"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_panel:dashboard')  # <-- FIXED
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('admin_panel:dashboard')  # <-- FIXED
            else:
                messages.error(request, 'You do not have admin permissions.')
        else:
            messages.error(request, 'Invalid admin credentials.')
    
    return render(request, 'admin/login.html')

def admin_logout(request):
    """Admin logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('admin_panel:login')  # <-- FIXED