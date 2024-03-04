from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from . models import UserProfile,Follow

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

def logout(request):
    response = redirect(login)
    response.delete_cookie('state')
    response.delete_cookie('user')
    return response

def home(request):
    try:
        state_cookie = request.COOKIES.get('state')
        user_cookie = request.COOKIES.get('user')
    except:
        return redirect(login)    
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
            "name":user_cookie
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

def get_user_details(request):
    try:
        current_user_name = request.COOKIES.get('user')
        current_user = User.objects.get(username=current_user_name)
        current_user_profile = UserProfile.objects.get(user=current_user)
        followers = Follow.objects.filter(following=current_user_profile)
        followings = Follow.objects.filter(follower=current_user_profile)
        print(followers,followings)
        user_data = []

        for user_profile in UserProfile.objects.all():
            profile_url = None
            if user_profile.profile:
                profile_url = user_profile.profile.url

            follower_profiles = [follower.follower.user.username for follower in followers]
            following_profiles = [following.following.user.username for following in followings]

            user_data.append({
                'name': user_profile.user.username,
                'bio': user_profile.bio,
                'profile': profile_url,
                'follower_profiles': follower_profiles,
                'following_profiles':following_profiles
            })
        print(follower_profiles)
        return JsonResponse(user_data, safe=False)

    except User.DoesNotExist:
        return JsonResponse({'error': 'Current user does not exist'}, status=400)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User profile does not exist'}, status=400)

def follow(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        account_name = data.get('accountName')
        follow_value = data.get('followResponse')
        print("===========", follow_value)
        current_user_name = request.COOKIES.get('user')
        try:
            current_user = User.objects.get(username=current_user_name)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Current user does not exist'}, status=400)
        try:
            user_to_follow = User.objects.get(username=account_name)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User to follow does not exist'}, status=400)
        try:
            current_user_profile = UserProfile.objects.get(user=current_user)
            user_to_follow_profile = UserProfile.objects.get(user=user_to_follow)
            print(current_user_profile,user_to_follow_profile)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile does not exist'}, status=400)

        if follow_value == 'Follow':
            follow_instance, created = Follow.objects.get_or_create(
                follower=current_user_profile,
                following=user_to_follow_profile
            )
            follow_instance.follow_value = follow_value
            follow_instance.save()
            if created:
                message = f'Now following {account_name}.'
            else:
                message = f'Follow relationship updated for {account_name}.'
        elif follow_value == 'Un Follow':
            try:
                Follow.objects.filter(follower=current_user_profile, following=user_to_follow_profile).delete()
                message = f'Unfollowed {account_name}.'
            except Exception as e:
                print("+++++main",e)
                message = f'Unfollowed {account_name}.'
        else:
            print("ok")
            message = 'Invalid follow response.'

        return JsonResponse({'message': message})

    return JsonResponse({'error': 'Invalid request'}, status=400)
