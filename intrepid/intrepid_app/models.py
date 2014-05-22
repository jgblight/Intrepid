import datetime
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagespecs import Pin_Display


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

    def get_hometown(self):
        if self.hometown:
            return self.hometown.name
        else:
            return ""

    def get_name(self): 
        if self.user.first_name:
            return self.user.first_name + " " + self.user.last_name
        else:
            return self.user.username

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
    text = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return "http://placekitten.com/500/300"

    def start(self):
        first_pin = self.pin_set.first()
        if first_pin:
            return first_pin.pin_date.date()
        else:
            return '???'

    def end(self):
        last_pin = self.pin_set.last()
        if last_pin:
            return last_pin.pin_date.date()
        else:
            return '???'

    def pins(self):
        return self.pin_set.order_by("pin_date")


    def pins_reverse(self):
        return self.pin_set.order_by("-pin_date")

class Pin(models.Model):
    trip = models.ForeignKey(Trip)
    name = models.CharField(max_length=200)
    pin_date = models.DateTimeField(default=datetime.datetime.today())
    location = models.ForeignKey(Location)
    tracks = models.BooleanField(default=False)
    text = models.TextField()

class Media(models.Model):
    pin = models.ForeignKey(Pin,blank=True,null=True)
    caption = models.CharField(max_length=200,blank=True)

class Image(Media):
    media = models.ImageField(upload_to="post_data")
    pin_display = ImageSpecField(source='media', id="pin_display")

