import datetime
import simplejson
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from intrepid_app.models import Profile,Trip, Pin,Location,Media,Image
from django.http import HttpResponse
import forms
import sys

@login_required
def index_view(request):
    if request.user.is_authenticated():
        return redirect('/profile/' + str(request.user.username))
    else:
        return redirect('/login')

def trip_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    pins = trip.pins()

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

def signup_view(request):
    if request.method == "POST":
        form = forms.SignupForm(request.POST)
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
        form = forms.SignupForm()
    return render(request, 'signup.html', {
        'form': form
        })

@login_required
def new_trip_view(request):
    if request.method == "POST":
        form = forms.TripForm(request.POST,request.FILES)
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
        form = forms.TripForm()
    return render(request, 'new_trip.html', {
        'form': form
        })

@login_required
def new_post_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if request.user != trip.user:
        return redirect("/")
    if request.method == "POST":
        form = forms.NewPostForm(request.POST)
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
        form = forms.NewPostForm()
    return render(request, 'new_post.html', {
        'trip' : trip ,
        'form': form
        })

def file_upload_view(request):
    if request.method == "POST":
        new_file = request.FILES[u'files[]']
        try:
            media = Image(media=new_file)
            media.save()
            result = [{'id':media.id,
                        'name':new_file.name},]
        except TypeError as e:
            print e
            result = [{"error":"Please upload a valid image"}]

        response_data = simplejson.dumps(result)
        return HttpResponse(response_data, mimetype='application/json')
    else:
        pass #return

@login_required
def edit_profile_view(request,username):
    if not username == request.user.username:
        return redirect("/profile/" + username)
    if request.method == "POST":
        form = forms.EditProfileForm(request.POST,request.FILES)
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
        form = forms.EditProfileForm()
    return render(request, 'edit_profile.html', {
        'profile_user' : User.objects.get(username=username),
        'form' : form 
    })

