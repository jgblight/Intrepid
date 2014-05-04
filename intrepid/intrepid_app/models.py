from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    name = models.CharField(max_length=200)

class Profile(models.Model):
    user = models.OneToOneField(User)
    hometown = models.ForeignKey(Location)
    text = models.TextField()
    created = models.DateTimeField(auto_now=True)

class Trip(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    text = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True,null=True)

class Pin(models.Model):
    trip = models.ForeignKey(Trip)
    name = models.CharField(max_length=200)
    pin_date = models.DateTimeField()
    location = models.ForeignKey(Location)
    tracks = models.BooleanField(default=False)
    text = models.TextField()
