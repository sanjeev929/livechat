from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from . models import UserProfile
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            return render(request, 'register.html', {'error_message': 'Passwords do not match'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error_message': 'Email is already registered'})
        existing_user = User.objects.filter(username=username).exists()
        if existing_user:
            return render(request, 'register.html', {'error_message': 'Email is already taken'})
        user = User.objects.create_user(email=email, username=username, password=password)
        return redirect('login')

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        state=False
        user = authenticate(request, username=username, password=password)
        print(username,password,user)
        if user is not None:
            state=True
            email = user.email
            print(email)
            response = redirect(home)
            response.set_cookie('state', state)
            response.set_cookie('user', user)
            return response
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    return render(request, 'login.html')

def home(request):
    state_cookie = request.COOKIES.get('state')
    user_cookie = request.COOKIES.get('user')
    if state_cookie and user_cookie:
        user = User.objects.get(username=user_cookie)
        email = user.email
        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            bio = user_profile.bio
            profile = user_profile.profile
        except:
            bio=None
            profile=None

        context={
            "email":email,
            "bio":bio,
            "profile":profile,
        }
        return render(request,"home.html",context)
    else:
        return render(request,"login.html")
    
def submitbio(request):
    user_cookie = request.COOKIES.get('user')
    if request.method == 'POST':
        email = request.POST['email']  
        bio = request.POST['bio'] 
        profile = request.POST['profile']
        user = User.objects.get(email=email)
        user.userprofile.bio = bio
        user.userprofile.profile = profile
        user.userprofile.save()
        return redirect(home)

    return redirect(home)
