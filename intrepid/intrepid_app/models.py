from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from imagekit import ImageSpec, register
from imagekit.models import ImageSpecField
from imagekit.processors import Crop
from imagekit.utils import get_field_info

# Create your models here.

class Profile_Image(ImageSpec):
    format = 'JPEG'
    options = {'quality': 60}

    @property 
    def processors(self):
        model, field_name = get_field_info(self.source)
        return [Crop(width=model.width,height=model.width,x=model.x,y=model.y)]

register.generator('profile_image', Profile_Image)

class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    name = models.CharField(max_length=200)

class Profile(models.Model):
    user = models.OneToOneField(User)
    image_file = models.ImageField(upload_to="profile",blank=True,null=True)
    image = ImageSpecField(source='image_file',id='profile_image')
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    width = models.IntegerField(default=500)
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
