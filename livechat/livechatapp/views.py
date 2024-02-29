from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            return render(request, 'register.html', {'error_message': 'Passwords do not match'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error_message': 'email is already register'})
        user = User.objects.create_user(username=email, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'register.html')

def home(request):
    return render(request,"home.html")