from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile = models.ImageField(upload_to='static/image', blank=True)

    def __str__(self):
        return self.user.username
    
class Follow(models.Model):
    follower = models.ForeignKey(UserProfile, related_name='follower', on_delete=models.CASCADE)
    following = models.ForeignKey(UserProfile, related_name='following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    follow = models.CharField(max_length=255)
    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.user.username} follows {self.following.user.username}'

class FollowAction(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    follow_instance = models.ForeignKey(Follow, on_delete=models.CASCADE)  # Rename to avoid conflict
    action = models.CharField(max_length=10)  # 'accept' or 'decline'

    def __str__(self):
        return f'{self.action} action for {self.user_profile}'