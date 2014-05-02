from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    name = models.CharField(max_length=200)

class Profile(models.Model):
    hometown = models.ForeignKey(Location)
    text = models.TextField()
    user = models.OneToOneField(User)

class Trip(models.Model):
    name = models.CharField(max_length=200)
    text = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user = models.ForeignKey(User)

class Pin(models.Model):
    name = models.CharField(max_length=200)
    pin_date = models.DateTimeField()
    location = models.ForeignKey(Location)
    tracks = models.BooleanField(default=False)
    text = models.TextField()
    trip = models.ForeignKey(Trip)
