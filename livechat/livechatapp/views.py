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
        if user is not None:
            state=True
            email = user.email
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
            parts = str(profile).split('/')
            # Remove the first part ('static') and the second part ('image')
            new_path = '/'.join(parts[2:])

        except:
            bio=None
            new_path=None
            profile=None
        context={
            "email":email,
            "bio":bio,
            "new_path":new_path,
            "profile":profile,
        }
        return render(request,"home.html",context)
    else:
        return render(request,"login.html")
    
def submitbio(request):
    user_cookie = request.COOKIES.get('user')
    if request.method == 'POST':
        bio = request.POST.get('bio')
        try:
            profile = request.FILES['profile']
        except: 
            profile = 5
        try:
            user = User.objects.get(username=user_cookie)
            email=user.email
            user = User.objects.get(email=email)
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.bio = bio
            if profile != 5:
                user_profile.profile = profile
            else:
                pass
            user_profile.save()
        except User.DoesNotExist:
            # Handle the case where the user with the provided email does not exist
            pass
        except UserProfile.DoesNotExist:
            # Handle the case where the user profile for the user does not exist
            pass
        return redirect(home)

    return redirect(home)
