from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns=[
    path("",views.home,name="home"),
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
    path("register/",views.register,name="register"),
    path("submitbio/",views.submitbio,name="submitbio"),
    path('get_user_details/', views.get_user_details, name='get_user_details'),
    path("follow/",views.follow,name="follow"),
    path('accept-decline-follow/',views.accept_decline_follow_view, name='accept_decline_follow_view'),
]