import re
import datetime
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from intrepid_app.models import Profile,Trip, Pin,Location
from django import forms
from django.forms.extras import SelectDateWidget


# Create your views here.

class SignupForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
    username = forms.CharField(label="Username",max_length=100)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Password",
        widget=forms.PasswordInput)
    password2 = forms.CharField(label="Re-type Password",
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
    name = forms.CharField(label="Title",max_length=200)
    description = forms.CharField(label="Description",widget=forms.Textarea,required=False)

@login_required
def new_trip_view(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            new_trip = Trip(name=name,text=description,user=request.user)
            new_trip.save()
            return redirect(index_view) #TODO: should redirect to trip page
    else:
        form = TripForm()
    return render(request, 'new_trip.html', {
        'form': form
        })

class NewPostForm(forms.Form):
    name = forms.CharField(label="Title",max_length=200)
    trip = forms.CharField(label="Trip")
    loc_name = forms.CharField(label="Location")
    lat = forms.FloatField(widget=forms.HiddenInput)
    lon = forms.FloatField(widget=forms.HiddenInput)
    tracks = forms.BooleanField(label="Make Tracks?",widget=forms.CheckboxInput,required=False)
    date = forms.DateField(label="Start Date",initial=datetime.date.today(),widget=SelectDateWidget)
    description = forms.CharField(label="Description",widget=forms.Textarea,required=False)

    def __init__(self, user, *args, **kwargs):
        super(NewPostForm, self).__init__(*args, **kwargs)
        self.fields['trip'] = forms.ChoiceField(label="Trip",choices=[ (o.id, o.name) for o in Trip.objects.filter(user=user)])

@login_required
def new_post_view(request):
    if request.method == "POST":
        form = NewPostForm(request.user,request.POST)
        if form.is_valid():
            lat = form.cleaned_data['lat']
            lon = form.cleaned_data['lon']
            location_name = form.cleaned_data['loc_name']
            location = Location(lat=lat,lon=lon,name=location_name)
            location.save()

            trip = Trip.objects.get(pk=form.cleaned_data['trip'])
            name = form.cleaned_data['name']
            pin_date = form.cleaned_data['date']
            tracks = form.cleaned_data['tracks']
            text = form.cleaned_data['description']
            pin = Pin(trip=trip,name=name,pin_date=pin_date,location=location,tracks=tracks,text=text)
            pin.save()
            return redirect(index_view) #TODO: should redirect to trip page
    else:
        form = NewPostForm(request.user)
    return render(request, 'new_post.html', {
        'form': form
        })


@login_required
def index_view(request):
    return render(request, 'index.html', {
        'user': request.user,
    })

@login_required
def trip_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    pins = trip.pin_set.all()

    center_lat = 0.0;
    center_lon = 0.0;
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

