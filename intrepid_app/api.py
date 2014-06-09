from piston.handler import BaseHandler
from piston.utils import rc, throttle
from intrepid_app.models import Trip,User,Pin,Location
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings
from dateutil.parser import parse
import datetime
import json

import sys


def http_basic_auth(func):
    def _wrapped_view_func(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return func(request, *args, **kwargs)

        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="Intrepid"'
        return response
    return _wrapped_view_func

@http_basic_auth
def active_trips(request,username):
    trips = Trip.objects.filter(user__username=username).filter(active=True).values("id","name")
    return HttpResponse(json.dumps(list(trips)), mimetype='application/json')

@csrf_exempt
@http_basic_auth
def new_pin_api(request): 
    if request.method == "POST":
        try:
            trip = Trip.objects.get(pk=int(request.GET.get('trip')));
        except:
            response = { 'success' : False, 'error' : 'Invalid Trip ID' }
        
        try:
            lat = float(request.GET.get('lat').decode('ascii','ignore'))
            lon = float(request.GET.get('lon').decode('ascii','ignore'))
            loc_name = request.GET.get('loc_name')
            location = Location(lat=lat,lon=lon,name=loc_name)
            location.save()
        except:
            response = { 'success' : False, 'error' : 'Problem with location' }

        name = request.GET.get('name')
        pin_date = parse(request.GET.get('date'))
        tracks = (request.GET.get('tracks') == "true")
        text = request.GET.get('text')     
        try:
            pin = Pin(trip=trip,name=name,pin_date=pin_date,location=location,tracks=tracks,text=text)
            pin.save()
            response = { 'success' : True }
        except:
            response = { 'success' : False, 'error' : 'Could not create pin' }
    else:
        response = { 'success' : False, 'error' : 'Use POST' }

    return HttpResponse(json.dumps(response), mimetype='application/json')



