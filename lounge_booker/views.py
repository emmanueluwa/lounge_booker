from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import Lounge
from .forms import UserForm

def home_page(request):
    if not request.user.is_authenticated:
        return redirect("lounge_booker:login")
    
    context = {"lounges": Lounge.objects.all()}
    return render(request, "home.html", context=context)


def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")   
            user = authenticate(username=username, password=password) 
            if user is not None:
                login(request, user)
                messages.info(request, f"Hello {username}, you are now logged in.")
                return redirect("lounge_booker:home")
            else:
                messages.error(request, "Invalid username or password, please try again.")
        else:
            messages.error(request, "Invalid username or password, please try again.")
    form = AuthenticationForm()
    return render(
        request=request, template_name="login.html", context={"login_form": form},
    )

def signup_page(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your registration was succesful, thank you.")
            return redirect("lounge_booker:home")
        messages.error(request, "Unsuccesful registration. Invalid Information, please try again.")
    form = UserForm
    return render(
        request=request,
        template_name="signup.html",
        context={"register_form": form},
        )



def logout_page(request):
    logout(request)
    messages.info(request, "You have logged out succesfully, see you soon.")
    return redirect("lounge_booker:login") 

