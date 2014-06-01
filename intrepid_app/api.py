from piston.handler import BaseHandler
from piston.utils import rc, throttle

from intrepid_app.models import Trip,User

class ActiveTripHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id','name')
    model = Trip

    def read(self, request, username):
        active_trips = Trip.objects.filter(user__username=username).filter(active=True)
        return active_trips
