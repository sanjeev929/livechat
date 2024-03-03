from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistration(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile = models.ImageField(upload_to='static/image', blank=True)

    def __str__(self):
        return self.user.username
