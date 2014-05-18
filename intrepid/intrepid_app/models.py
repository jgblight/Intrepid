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
        min_dim = min(model.image_file.width,model.image_file.height)
        return [Crop(width=min_dim,
                    height=min_dim,
                    x=int(-1*model.image_x*model.image_file.width),
                    y=int(-1*model.image_y*model.image_file.height))]

register.generator('profile_image', Profile_Image)

class Header_Image(ImageSpec):
    format = 'JPEG'
    options = {'quality': 60}

    @property 
    def processors(self):
        model, field_name = get_field_info(self.source)
        x = int(-1*model.image_x*model.image_file.width)
        y = int(-1*model.image_y*model.image_file.height)
        crop_width = int(model.image_width*model.image_file.width)
        crop_height = model.image_file.height + y
        return [Crop(width=crop_width,
                    height=crop_height,
                    x=x,
                    y=y)]

register.generator('header_image', Header_Image)

class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    name = models.CharField(max_length=200)

class Profile(models.Model):
    user = models.OneToOneField(User)
    image_file = models.ImageField(upload_to="profile",blank=True,null=True)
    image = ImageSpecField(source='image_file',id='profile_image')
    image_x = models.FloatField(default=0)
    image_y = models.FloatField(default=0)
    hometown = models.ForeignKey(Location,blank=True,null=True)
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now=True)

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return "http://placekitten.com/400/400"


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        profile = Profile(user=user)
        profile.save()

post_save.connect(create_profile,sender=User)

class Trip(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    image_file = models.ImageField(upload_to="profile",blank=True,null=True)
    image = ImageSpecField(source='image_file',id='header_image')
    image_x = models.FloatField(default=0)
    image_y = models.FloatField(default=0)
    image_width = models.FloatField(default=1)
    text = models.TextField()
    active = models.BooleanField(default=True)

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return "http://placekitten.com/500/300"

class Pin(models.Model):
    trip = models.ForeignKey(Trip)
    name = models.CharField(max_length=200)
    pin_date = models.DateTimeField()
    location = models.ForeignKey(Location)
    tracks = models.BooleanField(default=False)
    text = models.TextField()

class Media(models.Model):
    pin = models.ForeignKey(Pin,blank=True,null=True)
    media = models.FileField(upload_to="post_data")
    caption = models.CharField(max_length=200,blank=True)
