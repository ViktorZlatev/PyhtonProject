from xmlrpc.client import Boolean
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pic = models.ImageField(upload_to="img", blank=True, null=True)
    friends = models.ManyToManyField('Friend')
    
    def __str__(self):
        return self.name
    
    
class Friend(models.Model):
    friend_profile = models.OneToOneField(Profile, on_delete=models.CASCADE , default="")
    
    def __str__(self):
        return self.friend_profile.name