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
def profile_table():
    cursor.execute("""
                        CREATE TABLE profile (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(150) UNIQUE,
                            bio TEXT,
                            profile_picture BYTEA,
                            followersrequest VARCHAR[],
                            followingrequest VARCHAR[],      
                            freinds  VARCHAR[]
                        )
                    """)
    connection.commit()
    return "created"
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
        try:
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
            elif row:
                bio=row[0]
                profile_picture=None
            context={
            "name":user_cookie,
            "bio":bio,
            "profile":profile_picture
        }  
            return render(request,"home.html",context)
        except:
            try:
                cursor.execute("""
                    SELECT bio
                    FROM profile
                    WHERE username = %s
                    """, (user_cookie,))
                row = cursor.fetchone()
                if row:
                    bio=row[0]
                    profile_picture=None
                return render(request,"home.html",context)
            except:
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
                    profile_table()
                    profile_picture_content = profile_picture.read()
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
                    print(bio,profile_picture)
                    profile_picture_content = profile_picture.read()
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
                if not table_exists('profile'):
                    profile_table()
                    cursor.execute("""
                        INSERT INTO profile (username, bio)
                        VALUES (%s, %s)
                        ON CONFLICT (username) DO UPDATE
                        SET bio = EXCLUDED.bio
                    """, (user_cookie, bio))
                    connection.commit()
                else:
                    cursor.execute("""
                        INSERT INTO profile (username, bio)
                        VALUES (%s, %s)
                        ON CONFLICT (username) DO UPDATE
                        SET bio = EXCLUDED.bio
                    """, (user_cookie, bio))
                    connection.commit()
          
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
    followbtn=True
    try:
        try:
            current_user_name = request.COOKIES.get('user')
            current_user = User.objects.get(username=current_user_name)
            current_user_profile = UserProfile.objects.get(user=current_user)
            follows = Follow.objects.filter(follower=current_user_profile)

        
            for follow_instance in follows:
                followed_user_profile = follow_instance.following
                followed_users.append({
                    'username': followed_user_profile.user.username,
                    'profile_url': followed_user_profile.profile.url
                })
        except:
            pass
        try:
            current_user_name = request.COOKIES.get('user')
            cursor.execute("""
                    SELECT followersrequest
                    FROM profile
                    WHERE username = %s
                """, (current_user_name,))
            results = cursor.fetchall()
            for name in results[0][0]:
                print("name",name)
                cursor.execute("""
                    SELECT username, CASE 
                            WHEN profile.profile_picture IS NULL THEN 'Not' 
                            ELSE encode(profile.profile_picture, 'base64') 
                        END AS profile_picture
                    FROM profile
                    WHERE username = %s
                """, (name,))
                results = cursor.fetchall()

                for row in results:
                    username = row[0]
                    profile_picture = row[1]
                    # print("checking",username,profile_picture)
                follow_data.append({
                            'username': username,
                            "profile_url":profile_picture
                        })  
                
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
            #     user_data = {
            #     'name': name,
            #     'bio': bio,
            #     'prfile':profile_picture
            # }
            try:
                current_user_name = request.COOKIES.get('user')
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
                cursor.execute("""
                    SELECT profile.followingrequest
                    FROM auth_user
                    LEFT JOIN profile ON auth_user.username = profile.username
                    WHERE auth_user.username = %s;
                """, (current_user_name,))
                results1 = cursor.fetchall()
                
                for row in results:
                    name, bio, profile_picture = row
                    for data in results1:
                        if data[0] is not None:
                            if name in data[0]:
                                followbtn=False
                            else:
                                followbtn=True   
                    print(name,followbtn)                  
                    try:
                        if isinstance(profile_picture, memoryview):
                            profile_picture = profile_picture.tobytes()
                        user_data.append({
                            'name': name,
                            'bio': bio,
                            'profile':base64.b64encode(profile_picture).decode('utf-8'),
                            'followbtn':followbtn
                        })
                    except:
                        user_data.append({
                            'name': name,
                            'bio': bio,
                            'profile':profile_picture,
                            'followbtn':followbtn
                        })   
            except:
                try:
                    print("inside")
                    cursor.execute("""
                    SELECT username FROM auth_user""")
                    results = cursor.fetchall()
                    cursor.execute("""
                    SELECT 
                        profile.followingrequest
                    FROM 
                        auth_user
                    LEFT JOIN 
                        profile ON auth_user.username = profile.username
                    WHERE 
                        auth_user.username = profile.username;
                                """)
                    results1 = cursor.fetchall()
                    for row in results:
                        name = row[0]
                        for data in results1:
                            print(data[0])
                            if data[0] is not None:
                                if name in data[0]:
                                    followbtn=False
                                else:
                                    followbtn=True        
                        user_data.append({
                                    'name': name,
                                    'bio': "None",
                                    'profile':"Not",
                                    'followbtn':followbtn
                                })
                except:
                    cursor.execute("""
                    SELECT username FROM auth_user""")
                    results = cursor.fetchall()
                    for row in results:
                        name = row[0]   
                        user_data.append({
                                    'name': name,
                                    'bio': "None",
                                    'profile':"Not",
                                    'followbtn':followbtn      
                                })
        except Exception as e:
            pass
        print(user_data)
        return JsonResponse({'user_data': user_data, 'follow_data':follow_data })
    except Exception as e:
        return redirect("/")    


def follow1(current_user_name,follow_value,account_name):
    # Following Request=====================================================================
            existing_following_requests=[]
            cursor.execute("""
                    SELECT followingrequest
                    FROM profile
                    WHERE username = %s
                """, (current_user_name,))
            try:
                existing_following_requests = cursor.fetchone()[0]
            except:
                pass
           
            if existing_following_requests is None:
                existing_following_requests = []
            existing_following_requests.append(account_name)
            existing_following_requests=list(set(existing_following_requests))
            cursor.execute("""
                INSERT INTO profile (username, followingrequest)
                VALUES (%s, %s)
                ON CONFLICT (username)
                DO UPDATE SET followingrequest = %s
            """, (current_user_name, existing_following_requests, existing_following_requests))
            connection.commit()

            # Follow Request====================================================================
            existing_follow_requests=[]
            cursor.execute("""
                    SELECT followersrequest
                    FROM profile
                    WHERE username = %s
                """, (account_name,))
            try:
                existing_follow_requests = cursor.fetchone()[0]
            except:
                pass
    
            if existing_follow_requests is None:
                existing_follow_requests = []
            existing_follow_requests.append(current_user_name)
            existing_follow_requests=list(set(existing_follow_requests))
            cursor.execute("""
                INSERT INTO profile (username, followersrequest)
                VALUES (%s, %s)
                ON CONFLICT (username)
                DO UPDATE SET followersrequest = %s
            """, (account_name, existing_follow_requests, existing_follow_requests))
            connection.commit()

def follow(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        account_name = data.get('accountName')
        follow_value = data.get('followResponse')
        current_user_name = request.COOKIES.get('user')
        if follow_value == 'Follow':
            if not table_exists('profile'):
                profile_table()
                follow1(current_user_name,follow_value,account_name)
            else:
                follow1(current_user_name,follow_value,account_name)
        elif follow_value == 'Un Follow':
            cursor.execute("""
                    SELECT followersrequest
                    FROM profile
                    WHERE username = %s
                """, (account_name,))
            existing_follow_requests = cursor.fetchone()[0]
            if existing_follow_requests is None:
                existing_follow_requests = []
                existing_follow_requests.remove(current_user_name)

        else:
            pass
        message='OK'

        return JsonResponse({'message': message})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def accept_decline_follow_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            username = data.get('username')
            action = data.get('action')
            # Retrieve the current user's profile
            current_user_name = request.COOKIES.get('user')
            current_user = User.objects.get(username=current_user_name)
            current_user_profile = UserProfile.objects.get(user=current_user)
            # Retrieve the follower's profile
            try:
                followe_user = User.objects.get(username=username)
                follower_profile = UserProfile.objects.get(user=followe_user)
            except Exception as e:  
            # Retrieve the follow instance
                pass
            try:    
                follow_instance = get_object_or_404(Follow, follower=follower_profile, following=current_user_profile)
            except Exception as e:  
                pass
            if action == 'accept':
                
                # Create a new FollowAction for accepting the follow request
                try:
                    FollowAction.objects.create(user_profile=current_user_profile,follow=follow_instance, action='accept')
                except Exception as e:
                    pass
                follow_instance.delete()
            elif action == 'decline':
                # Delete the follow relationship if it is declined
                follow_instance.delete()
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)

            return JsonResponse({'success': True})
        except Http404:
            return JsonResponse({'error': 'User or follow relationship not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)