import re
import datetime
import simplejson
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from intrepid_app.models import Profile,Trip, Pin,Location,Media
from django import forms
from django.forms.extras import SelectDateWidget
from django.http import HttpResponse
from django.db.utils import *
import sys

# Create your views here.

class SignupForm(forms.Form):
    username = forms.CharField(label="Username",max_length=100)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Password",
        widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password",
        widget=forms.PasswordInput)

    error_messages = {
        'duplicate_email': "Email already registered",
        'password_mismatch': "The two password fields didn't match",
        'invalid_email': "Not a valid email address"
    }

    def clean(self):
        email = self.cleaned_data.get("email")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError(
                self.error_messages['invalid_email'],
                code='invalid_email',
            )

        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).count():
            raise forms.ValidationError(
                self.error_messages['duplicate_email'],
                code='duplicate_email',
            )

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return self.cleaned_data

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():

            # create user and authenticate
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            user = User.objects.create_user(username, email, password)
            user.save()
            user = authenticate(username=username,password=password)
            login(request, user)
            return redirect(index_view)
    else:
        form = SignupForm()
    return render(request, 'signup.html', {
        'form': form
        })

class TripForm(forms.Form):
    image = forms.ImageField(required=False)
    image_x = forms.FloatField(required=False,widget=forms.HiddenInput)
    image_y = forms.FloatField(required=False,widget=forms.HiddenInput)
    image_width = forms.FloatField(required=False,widget=forms.HiddenInput)
    name = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'placeholder': 'Trip Title'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':30, 'placeholder':'Enter a description'}),required=False)

@login_required
def new_trip_view(request):
    if request.method == "POST":
        form = TripForm(request.POST,request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            if request.FILES.has_key('image'):
                image_file = request.FILES['image']
            else:
                image_file = None

            x = form.cleaned_data['image_x'] if form.cleaned_data['image_x'] else 0
            y = form.cleaned_data['image_y'] if form.cleaned_data['image_y'] else 0
            image_width = form.cleaned_data['image_width'] if form.cleaned_data['image_width'] else 1

            new_trip = Trip(name=name,text=description,user=request.user,image_file=image_file,image_x=x,image_y=y,image_width=image_width)
            new_trip.save()
            return redirect('/trip/'+str(new_trip.id)+'/post')
    else:
        form = TripForm()
    return render(request, 'new_trip.html', {
        'form': form
        })

class NewPostForm(forms.Form):
    name = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'placeholder': 'Post Title'}))
    loc_name = forms.CharField()
    lat = forms.FloatField(widget=forms.HiddenInput)
    lon = forms.FloatField(widget=forms.HiddenInput)
    tracks = forms.BooleanField(label="Make Tracks?",widget=forms.CheckboxInput,required=False)
    date = forms.DateField(initial=datetime.date.today(),widget=SelectDateWidget)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':30, 'placeholder':'Enter a description'}),required=False)

@login_required
def new_post_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if request.method == "POST":
        form = NewPostForm(request.POST)
        print request.POST
        if form.is_valid():
            lat = form.cleaned_data['lat']
            lon = form.cleaned_data['lon']
            location_name = form.cleaned_data['loc_name']
            location = Location(lat=lat,lon=lon,name=location_name)
            location.save()

            name = form.cleaned_data['name']
            pin_date = form.cleaned_data['date']
            tracks = form.cleaned_data['tracks']
            text = form.cleaned_data['description']
            pin = Pin(trip=trip,name=name,pin_date=pin_date,location=location,tracks=tracks,text=text)
            pin.save()

            for media_id in request.POST.getlist('uploads',[]):
                media = Media.objects.get(pk=int(media_id))
                media.pin = pin
                media.save()
            return redirect('/trip/'+str(trip_id)) 
    else:
        form = NewPostForm()
    return render(request, 'new_post.html', {
        'trip' : trip ,
        'form': form
        })

def file_upload_view(request):
    if request.method == "POST":
        new_file = request.FILES[u'files[]']
        media = Media(media=new_file)
        media.save()

        result = [{'id':media.id,
                    'name':new_file.name},]
        response_data = simplejson.dumps(result)
        return HttpResponse(response_data, mimetype='application/json')
    else:
        pass # handle errors

@login_required
def index_view(request):
    if request.user.is_authenticated():
        return redirect('/profile/' + str(request.user.username))
    else:
        return redirect('/login')

def trip_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    pins = trip.pin_set.all()

    center_lat = 0.0;
    center_lon = 0.0;
    if len(pins):
        for p in pins:
            center_lat += p.location.lat
            center_lon += p.location.lon
        center_lat /= len(pins)
        center_lon /= len(pins)

    return render(request, 'trip.html', {
        'trip' : trip,
        'pins' : pins,
        'center_lat' : center_lat,
        'center_lon' : center_lon
        })

def profile_view(request,username):
    return render(request, 'profile.html', {
        'profile_user' : User.objects.get(username=username),
        'edit' : username == request.user.username
    })

class EditProfileForm(forms.Form):
    image  = forms.ImageField(required=False)
    image_x = forms.FloatField(required=False,widget=forms.HiddenInput)
    image_y = forms.FloatField(required=False,widget=forms.HiddenInput)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    hometown_name = forms.CharField(required=False)
    lat = forms.FloatField(widget=forms.HiddenInput,required=False)
    lon = forms.FloatField(widget=forms.HiddenInput,required=False)
    text = forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'cols':30}),required=False)

@login_required
def edit_profile_view(request,username):
    if not username == request.user.username:
        return redirect("/profile/" + username)
    if request.method == "POST":
        form = EditProfileForm(request.POST,request.FILES)
        if form.is_valid():
            user = User.objects.get(username=username)
            profile = user.get_profile()

            lat = form.cleaned_data['lat']
            lon = form.cleaned_data['lon']
            location_name = form.cleaned_data['hometown_name']
            if lat and lon and location_name:
                location = Location(lat=lat,lon=lon,name=location_name)
                location.save()
                profile.hometown = location

            if form.cleaned_data['first_name']:
                user.first_name = form.cleaned_data['first_name']

            if form.cleaned_data['last_name']:
                user.last_name = form.cleaned_data['last_name']

            if form.cleaned_data['text']:
                profile.text = form.cleaned_data['text']

            if form.cleaned_data['image_x'] is not None and form.cleaned_data['image_y'] is not None:
                profile.image_x = form.cleaned_data['image_x']
                profile.image_y = form.cleaned_data['image_y']

            if request.FILES.has_key('image'):
                profile.image_file = request.FILES['image']

            profile.save()
            user.save()
            
            return redirect("/profile/" + username)
    else:
        form = EditProfileForm()
    return render(request, 'edit_profile.html', {
        'profile_user' : User.objects.get(username=username),
        'form' : form 
    })

