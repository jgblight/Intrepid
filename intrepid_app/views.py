import base64
import time
import os
import urllib
import hmac
import uuid
from hashlib import sha1
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from intrepid_app.models import Trip, Pin, Location, Image
from django.http import HttpResponse
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import forms
import json

@login_required
def index_view(request):
    if request.user.is_authenticated():
        return redirect('/profile/' + str(request.user.username))
    else:
        return redirect('/signup')

def trip_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    content = { 
                'trip' : trip,
                'edit' : trip.user.username == request.user.username }
    if request.GET.has_key('post'):
        if request.GET['post'] == 'last':
            content['post'] = trip.pin_set.count() - 1
        else:
            content['post'] = request.GET['post']
    return render(request, 'trip.html', content)

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
        return redirect(request.META.get("HTTP_REFERRER","/"))
    if request.method == "POST":
        form = forms.NewPostForm(request.POST)
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
            pin = Pin.objects.create(trip=trip,name=name,pin_date=pin_date,location=location,tracks=tracks,text=text)

            urls = request.POST.get("upload-urls").strip("|").split("|")

            for url in urls:
                image = Image.objects.create(pin=pin)
                img_temp = NamedTemporaryFile(delete = True)
                img_temp.write(urllib.urlopen(url).read())
                img_temp.flush()
                image.media.save(url.rsplit("/"), File(img_temp))

            return redirect('/trip/'+str(trip_id)+'?post=last') 
    else:
        form = forms.NewPostForm()
    return render(request, 'new_post.html', {
        'trip' : trip ,
        'form': form
        })

@login_required
def finish_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if request.user != trip.user:
        response = {'success':False}
    else:
        trip.active = False
        trip.save()
        response = {'success':True}
    response = json.dumps(response)
    return HttpResponse(response, mimetype='application/json')

@login_required
def reactivate_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if request.user != trip.user:
        response = {'success':False}
    else:
        trip.active = True
        trip.save()
        response = {'success':True}
    response = json.dumps(response)
    return HttpResponse(response, mimetype='application/json')

@login_required
def delete_trip_view(request,trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    if request.user != trip.user:
        response = {'success':False}
    else:
        pins = trip.pin_set.all()
        for p in pins:
            p.delete()
        trip.delete()
        response = {'success':True}
    response = json.dumps(response)
    return HttpResponse(response, mimetype='application/json')

@login_required
def delete_pin_view(request,pin_id):
    pin = get_object_or_404(Pin, pk=pin_id)
    if request.user != pin.trip.user:
        response = {'success':False}
    else:
        pin.delete()
        response = {'success':True}
    response = json.dumps(response)
    return HttpResponse(response, mimetype='application/json')


def sign_s3(request):
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID') or settings.AWS_ACCESS_KEY
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or settings.AWS_SECRET_KEY
    S3_BUCKET = os.environ.get('S3_BUCKET') or settings.S3_BUCKET

    object_name = request.user.username + str(uuid.uuid4()).replace("-","")
    mime_type = request.GET.get('s3_object_type')

    expires = long(time.time()+10)
    amz_headers = "x-amz-acl:public-read"

    put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)

    signature = base64.encodestring(hmac.new(AWS_SECRET_KEY, put_request, sha1).digest())
    signature = urllib.quote_plus(signature.strip())

    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)
    return HttpResponse(json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
         'url': url
      }), content_type='application/json')

@login_required
def file_upload_view(request):
    if request.method == "POST":
        files = request.FILES[u'files[]']
        if type(files) is not list:
            files = [files]

        result = []
        for new_file in files:
            content_type = new_file.content_type.split("/")[0]
            if content_type == "image":
                media = Image(media=new_file)
                media.save()
                result.append({'id':media.id,
                            'name':new_file.name,
                            'url':media.pin_display.url})
            else:
                result.append({"error" : new_file.name + " is not a valid image"})

        response_data = json.dumps(result)
        return HttpResponse(response_data, mimetype='application/json')
    else:
        pass #return 404

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

