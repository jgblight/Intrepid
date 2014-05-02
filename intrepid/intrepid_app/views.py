from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from intrepid_app.models import Profile
from django import forms

from crispy_forms.layout import Submit

# Create your views here.

def login_view(request):
    message = ''
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST) # A form bound to the POST data
        print form.errors
        if form.is_valid(): # All validation rules pass
            username = form.username
            password = form.password
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    redirect('index')
                else:
                    message = 'User not active'
            else:
                message = 'Username or password incorrect'
        else:
            message = 'invalid form'
    form = AuthenticationForm() # An unbound form

    return render(request, 'login.html', {
        'form': form,
        'message': message
    })

def signup_view(request):
    pass

@login_required
def index_view(request):
    return render(request, 'index.html', {
        'user': request.user,
    })

