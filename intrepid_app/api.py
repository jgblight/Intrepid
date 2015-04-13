from piston.handler import BaseHandler
from piston.utils import rc, throttle
from intrepid_app.models import Trip,User,Pin,Location,Image
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings
from dateutil.parser import parse
import datetime
import json
import logging
import sys

logger = logging.getLogger(__name__)


def http_basic_auth(func):
    def _wrapped_view_func(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        #if not request.is_secure():
        #    if getattr(settings, 'HTTPS_SUPPORT', True):
        #        request_url = request.build_absolute_uri(request.get_full_path())
        #        secure_url = request_url.replace('http://', 'https://')
        #        return HttpResponseRedirect(secure_url)
        logger.info(str(request.META))
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            logger.info(auth)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                logger.info(auth)
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
            trip = Trip.objects.get(pk=int(request.POST.get('trip')));
        except:
            response = { 'success' : False, 'error' : 'Invalid Trip ID' }

        try:
            lat = float(request.POST.get('lat').decode('ascii','ignore'))
            lon = float(request.POST.get('lon').decode('ascii','ignore'))
            location = Location.objects.create(lat=lat,lon=lon)
        except:
            response = { 'success' : False, 'error' : 'Problem with location' }

        name = request.POST.get('name')
        pin_date = parse(request.POST.get('date'))
        tracks = (request.POST.get('tracks') == "true")
        text = request.POST.get('text')     
        try:
            pin = Pin(trip=trip,name=name,pin_date=pin_date,location=location,tracks=tracks,text=text)
            pin.save()
        except:
            response = { 'success' : False, 'error' : 'Could not create pin' }

        try:
            for uploadedFile in request.FILES.itervalues():
                media = Image(media=uploadedFile,pin=pin)
                media.save()
            response = { 'success' : True }
        except:
            pin.delete()
            response = { 'success' : False, 'error' : 'Image upload failed' }
    else:
        response = { 'success' : False, 'error' : 'Use POST' }

    return HttpResponse(json.dumps(response), mimetype='application/json')



