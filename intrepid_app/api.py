from piston.handler import BaseHandler
from piston.utils import rc, throttle
from intrepid_app.models import Trip,User,Pin,Location
from django.views.decorators.csrf import csrf_exempt
from dateutil.parser import parse
import datetime

import sys

class CsrfExemptBaseHandler(BaseHandler):
            """
            handles request that have had csrfmiddlewaretoken inserted 
            automatically by django's CsrfViewMiddleware
 
            """
            def flatten_dict(self, dct):
                if 'csrfmiddlewaretoken' in dct:
                    # dct is a QueryDict and immutable
                    dct = dct.copy()  
                    del dct['csrfmiddlewaretoken']
                return super(CsrfExemptBaseHandler, self).flatten_dict(dct)

class ActiveTripHandler(CsrfExemptBaseHandler):
    allowed_methods = ('GET',)
    fields = ('id','name')
    model = Trip

    def read(self, request, username):
        active_trips = Trip.objects.filter(user__username=username).filter(active=True)
        return active_trips

class PinHandler(CsrfExemptBaseHandler):
    allowed_methods = ('GET',)
    model = Pin

    #should be 'create' need to fix fucky csrf stuff later
    def read(self,request): 
        try:
            try:
                trip = Trip.objects.get(pk=int(request.GET.get('trip')));
            except:
                return { 'success' : False, 'error' : 'Invalid Trip ID' }
            
            try:
                lat = float(request.GET.get('lat').decode('ascii','ignore'))
                lon = float(request.GET.get('lon').decode('ascii','ignore'))
                loc_name = request.GET.get('loc_name')
                location = Location(lat=lat,lon=lon,name=loc_name)
                location.save()
            except:
                return { 'success' : False, 'error' : 'Problem with location' }

            name = request.GET.get('name')
            pin_date = parse(request.GET.get('date'))
            tracks = (request.GET.get('tracks') == "true")
            text = request.GET.get('text')     
            try:
                pin = Pin(trip=trip,name=name,pin_date=pin_date,location=location,tracks=tracks,text=text)
                pin.save()
                return { 'success' : True }
            except:
                return { 'success' : False, 'error' : 'Could not create pin' }
        except:
            print sys.exc_info()

