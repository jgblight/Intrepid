import re
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from intrepid_app.models import Profile,Trip
from django import forms


# Create your views here.

class SignupForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
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

        if User.objects.filter(username=email).count():
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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            user = User.objects.create_user(email, email, password)
            user.save()
            user = authenticate(username=email,password=password)
            login(request, user)
            return redirect(index_view)
    else:
        form = SignupForm()
    return render(request, 'signup.html', {
        'form': form
        })

class TripForm(forms.Form):
    name = forms.CharField(label="Title",max_length=200)
    start = forms.DateField(label="Start Date",widget=forms.DateInput)
    description = forms.CharField(label="Description",widget=forms.Textarea)

@login_required
def new_trip_view(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            start = form.cleaned_data['start']
            description = form.cleaned_data['description']

            new_trip = Trip(name=name,text=description,start_date=start,user=request.user)
            new_trip.save()
            redirect("/") #TODO: should redirect to trip page
    else:
        form = TripForm()
    return render(request, 'new_trip.html', {
        'form': form
        })

class NewPostForm(forms.Form):
    name = forms.CharField(label="Title",max_length=200)
    trip = forms.CharField(label="Trip")
    tracks = forms.BooleanField(label="Make Tracks?",widget=forms.CheckboxInput)
    date = forms.DateField(label="Start Date",widget=forms.DateInput)
    description = forms.CharField(label="Description",widget=forms.Textarea)

    def __init__(self, user, *args, **kwargs):
        super(waypointForm, self).__init__(*args, **kwargs)
        self.fields['trip'] = forms.ChoiceField(label="Trip",choices=[ (o.id, str(o)) for o in Trip.objects.filter(user=user)])

@login_required
def new_post_view(request):
    if request.method == "POST":
        form = NewPostForm(request.user,request.POST)
        if form.is_valid():
            #process form
            redirect("/") #TODO: should redirect to trip page
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

