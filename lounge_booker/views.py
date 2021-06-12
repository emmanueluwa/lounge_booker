from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import Lounge

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
                messages.info(request, f"Welome {username}, you are now logged in.")
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
    return render(request, "signup.html", context={})


def logout_page(request):
    return render(request, "signup.html", context={})
