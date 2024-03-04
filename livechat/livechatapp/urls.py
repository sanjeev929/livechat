from django.urls import path
from . import views

urlpatterns=[
    path("",views.home,name="home"),
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
    path("register/",views.register,name="register"),
    path("submitbio/",views.submitbio,name="submitbio"),
    path('get_user_details/', views.get_user_details, name='get_user_details'),
]