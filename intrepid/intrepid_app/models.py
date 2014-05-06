from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

# Create your models here.

class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    name = models.CharField(max_length=200)

class Profile(models.Model):
    user = models.OneToOneField(User)
    hometown = models.ForeignKey(Location,blank=True,null=True)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now=True)

def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        profile = Profile(user=user)
        profile.save()

post_save.connect(create_profile,sender=User)

class Trip(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    text = models.TextField()
    active = models.BooleanField(default=True)

class Pin(models.Model):
    trip = models.ForeignKey(Trip)
    name = models.CharField(max_length=200)
    pin_date = models.DateTimeField()
    location = models.ForeignKey(Location)
    tracks = models.BooleanField(default=False)
    text = models.TextField()
