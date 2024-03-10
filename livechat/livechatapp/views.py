from django.shortcuts import render, redirect,get_object_or_404
import json
from django.http import JsonResponse,Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from . models import UserProfile,Follow,FollowAction

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
        try:
            user = User.objects.get(username=user_cookie)
        except:
            return redirect(login)
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
    followed_users = []
    user_data = []
    try:
        try:
            current_user_name = request.COOKIES.get('user')
            print(current_user_name)
            current_user = User.objects.get(username=current_user_name)
            current_user_profile = UserProfile.objects.get(user=current_user)
            follows = Follow.objects.filter(follower=current_user_profile)

        
            for follow_instance in follows:
                followed_user_profile = follow_instance.following
                followed_users.append({
                    'username': followed_user_profile.user.username,
                    'profile_url': followed_user_profile.profile.url
                })
            print("Followed users:", followed_users)
        except:
            pass
        try:
            current_user_name = request.COOKIES.get('user')
            current_user = User.objects.get(username=current_user_name)
            current_user_profile = UserProfile.objects.get(user=current_user)
            followers = Follow.objects.filter(following=current_user_profile)
            followings = Follow.objects.filter(follower=current_user_profile)

           
            follow_data = {
                'follower_profiles': [{'username': follower.follower.user.username, 'profile_url': follower.follower.profile.url} for follower in followers],
                'following_profiles': [{'username': following.following.user.username, 'profile_url': following.following.profile.url} for following in followings]
            }
        except:
            pass
        try:
            for user in User.objects.all():
                try:
                    # Retrieve associated profile for the user, if it exists
                    user_profile = UserProfile.objects.get(user=user)

                    # Extract profile information
                    profile_url = None
                    user_bio = None
                    
                    if user_profile.profile:
                        profile_url = user_profile.profile.url
                    
                    if user_profile.bio:
                        user_bio = user_profile.bio

                    # Append the data to user_data list
                    user_data.append({
                        'name': user.username,
                        'bio': user_bio,
                        'profile': profile_url,
                    })

                except UserProfile.DoesNotExist:
                    # If UserProfile does not exist for the user, only include username
                    user_data.append({
                        'name': user.username,
                        'bio': None,
                        'profile': None,
                    })

                except Exception as e:
                    print("Error processing user:", e)
        except:
            pass
        # Now user_data contains all the required information
        print(user_data)
        return JsonResponse({'user_data': user_data, 'follow_data':follow_data })
    except:
        return redirect("/")    

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

def accept_decline_follow_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            print("yesss")
            username = data.get('username')
            action = data.get('action')
            print("yesss1")
            # Retrieve the current user's profile
            current_user_name = request.COOKIES.get('user')
            current_user = User.objects.get(username=current_user_name)
            current_user_profile = UserProfile.objects.get(user=current_user)
            print("yesss2")
            # Retrieve the follower's profile
            try:
                print("111111111111111",username)
                followe_user = User.objects.get(username=username)
                follower_profile = UserProfile.objects.get(user=followe_user)
                print("22222222222",follower_profile)
            except Exception as e:
                print("perfect",e)      
            # Retrieve the follow instance
            try:    
                follow_instance = get_object_or_404(Follow, follower=follower_profile, following=current_user_profile)
            except Exception as e:
                print("perfect",e)   
            print("yesss3")
            if action == 'accept':
                print("yesss4")
                # Create a new FollowAction for accepting the follow request
                FollowAction.objects.create(follow=follow_instance, action='accept')
                follow_instance.delete()
            elif action == 'decline':
                print("yesss5")
                # Delete the follow relationship if it is declined
                follow_instance.delete()
            else:
                print("yesss6")
                return JsonResponse({'error': 'Invalid action'}, status=400)

            return JsonResponse({'success': True})
        except Http404:
            return JsonResponse({'error': 'User or follow relationship not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)