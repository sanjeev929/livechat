from django.shortcuts import render, redirect,get_object_or_404
import json
from django.http import JsonResponse,Http404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from . models import UserProfile,Follow,FollowAction
from django.db import connection
from django.db.utils import OperationalError
import base64

cursor = connection.cursor()
def table_exists(table_name):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = %s
        )
    """, (table_name,))
    return cursor.fetchone()[0]

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            return render(request, 'register.html', {'error_message': 'Passwords do not match'})
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'auth_user')")

           
            if not table_exists('auth_user'):
                cursor.execute("""
                    CREATE TABLE auth_user (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(150) UNIQUE,
                        email VARCHAR(254) UNIQUE,
                        password VARCHAR(128)
                    )
                """)
            cursor.execute("SELECT id FROM auth_user WHERE email = %s", [email])
            row = cursor.fetchone()
            if row:
                return render(request, 'register.html', {'error_message': 'Email is already registered'})
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM auth_user WHERE username = %s", [username])
                row = cursor.fetchone()
            if row:
                return render(request, 'register.html', {'error_message': 'Username is already taken'})
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO auth_user (username, email, password) VALUES (%s, %s, %s)", [username, email, password])
            
            return redirect('login')
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        cursor.execute("""
        SELECT username, password
        FROM auth_user
        WHERE username = %s AND password = %s
        """, (username, password))
        user = cursor.fetchone()
        print(user[0])
        if user is not None:
            response = redirect('home')
            response.set_cookie('user', user[0])
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
        user_cookie = request.COOKIES.get('user')
    except:
        return redirect(login)    
    if user_cookie:
        cursor.execute("""
            SELECT bio, profile_picture
            FROM profile
            WHERE username = %s
            """, (user_cookie,))
        row = cursor.fetchone()
        if row:
            bio = row[0]
            profile_picture = row[1]
            profile_picture = base64.b64encode(profile_picture).decode('utf-8')
            print(profile_picture)
        else:
            bio=None
            profile_picture=None    
        context={
            "name":user_cookie,
            "bio":bio,
            "profile":profile_picture
        }
        return render(request,"home.html",context)
    else:
        return redirect(login)
    
def submitbio(request):
    user_cookie = request.COOKIES.get('user')
    if request.method == 'POST':
        bio = request.POST.get('bio')
        try:
            profile_picture = request.FILES['profile']
        except: 
            profile_picture = 5
        try:
            if profile_picture != 5:
                if not table_exists('profile'):
                    cursor.execute("""
                        CREATE TABLE profile (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(150) UNIQUE,
                            bio TEXT,
                            profile_picture BYTEA,
                            followers VARCHAR[],
                            following VARCHAR[]
                        )
                    """)
                    connection.commit()
                else:
                    profile_picture_content = profile_picture.read()
                    # Ensure that profile_picture_content is bytes type
                    if not isinstance(profile_picture_content, bytes):
                        profile_picture_content = profile_picture_content.encode()
                    cursor.execute("""
                        INSERT INTO profile (username, bio, profile_picture)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (username) DO UPDATE
                        SET bio = EXCLUDED.bio,
                            profile_picture = EXCLUDED.profile_picture
                    """, (user_cookie, bio, profile_picture_content))
                    connection.commit()
            else:
                pass
          
        except User.DoesNotExist:
            pass
        except UserProfile.DoesNotExist:
           
            pass
        return redirect(home)

    return redirect(home)

def get_user_details(request):
    followed_users = []
    follow_data=[]
    user_data = []
    try:
        try:
            current_user_name = request.COOKIES.get('user')
            print("user",current_user_name)
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
            follower_profiles = []
            profile_url=None
            for follower in followers:
                try:
                    username = follower.follower.user.username
                    try:
                        profile_url = follower.follower.profile.url
                    except:
                        pass
                    print("follower",username)
                    profile = {
                        'username': username,
                        'profile_url': profile_url
                    }
                    follower_profiles.append(profile)
                except Exception as e:
                    print(f"Error fetching follower profile: {e}")

            following_profiles = []
            for following in followings:
                try:
                    username = following.following.user.username
                    print("following",username)
                    try:
                        profile_url = following.following.profile.url
                    except:
                        pass
                    profile = {
                        'username': username,
                        'profile_url': profile_url
                    }
                    following_profiles.append(profile)
                except Exception as e:
                    print(f"Error fetching following profile: {e}")

            # Construct the follow_data dictionary
            follow_data = {
                'follower_profiles': follower_profiles,
                'following_profiles': following_profiles
            }

        except:
            pass
        try:
            # cursor.execute("""
            #         SELECT auth_user.username, profile.bio, profile.profile_picture
            #         FROM auth_user
            #         INNER JOIN profile ON auth_user.username = profile.username
            #     """)
            # results = cursor.fetchall()

            # for row in results:
            #     name, bio, profile_picture = row
            #     print("=========================",name,bio,profile_picture)
            #     user_data = {
            #     'name': name,
            #     'bio': bio,
            #     'prfile':profile_picture
            # }
            cursor.execute("""
                SELECT 
                    auth_user.username, 
                    COALESCE(profile.bio, 'Not') AS bio, 
                    CASE 
                        WHEN profile.profile_picture IS NULL THEN 'Not' 
                        ELSE encode(profile.profile_picture, 'base64') 
                    END AS profile_picture
                FROM 
                    auth_user
                LEFT JOIN 
                    profile ON auth_user.username = profile.username
            """)
            results = cursor.fetchall()
            for row in results:
                name, bio, profile_picture = row
                print(name,profile_picture)
                try:
                    # Convert profile_picture to a suitable format for serialization
                    if isinstance(profile_picture, memoryview):
                        profile_picture = profile_picture.tobytes()  # Convert memoryview to bytes

                    # Append the row to the list after ensuring that all fields are serializable
                    user_data.append({
                        'name': name,
                        'bio': bio,
                        'profile':base64.b64encode(profile_picture).decode('utf-8')
                    })
                    print("ok")
                except:
                    user_data.append({
                        'name': name,
                        'bio': bio,
                        'profile':profile_picture
                    })   

        except Exception as e:
            pass
        return JsonResponse({'user_data': user_data, 'follow_data':follow_data })
    except Exception as e:
        print(e)
        return redirect("/")    

def follow(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        account_name = data.get('accountName')
        follow_value = data.get('followResponse')
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
            print("===========", follow_value,current_user,user_to_follow)
            try:
                current_user_profile = UserProfile.objects.get(user=current_user)
                user_to_follow_profile = UserProfile.objects.get(user=user_to_follow)
            except Exception as e:
                print(e)    
            print("===========", current_user_profile)
            print(current_user_profile,user_to_follow_profile,user_to_follow_profile)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile does not exist'}, status=400)
        if follow_value == "Follow":
            follow_instance, created = Follow.objects.get_or_create(
                follower=current_user_profile,
                following=user_to_follow_profile
            )
            follow_instance.follow = follow_value
            follow_instance.save()
            if created:
                print("ok created")
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
                print("perfecttt",e)      
            # Retrieve the follow instance
            try:    
                follow_instance = get_object_or_404(Follow, follower=follower_profile, following=current_user_profile)
            except Exception as e:
                print("perfect",e)   
            print("yesss3")
            if action == 'accept':
                print("yesss4")
                # Create a new FollowAction for accepting the follow request
                try:
                    FollowAction.objects.create(user_profile=current_user_profile,follow=follow_instance, action='accept')
                except Exception as e:
                    print("ssd",e)    
                print("yess5")
                follow_instance.delete()
            elif action == 'decline':
                print("yesss55")
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