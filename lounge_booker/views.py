from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Lounge, Booking
from .forms import UserForm, BookingForm

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
        messages.error(request, "Unsuccesful registration. Invalid information, please try again.")
    form = UserForm()
    return render(
        request=request,
        template_name="signup.html",
        context={"register_form": form},
        )



def logout_page(request):
    logout(request)
    messages.info(request, "You have logged out succesfully, see you soon.")
    return redirect("lounge_booker:login") 



def book_lounge(request, lounge_id):
    if not request.user.is_authenticated:
        return redirect("lounge_booker:login")

    try:
        lounge = Lounge.objects.get(id=lounge_id)
    except Lounge.DoesNotExist:
        lounge = None

    if lounge is None:
        messages.error(request, "This lounge is not available, please select another.")
        return redirect("lounge_booker:home")
    
    if request.method == "POST":
        form = BookingForm(lounge, request.POST)
         
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.lounge = lounge
            booking.save()
            messages.info(request, f"You have succesfully booked with {lounge}. Enjoy!")
            return redirect("lounge_booker:home")
    
    else:
        form = BookingForm(lounge)

    return render(request=request, template_name="book_lounge.html", context={"booking_form": form, "lounge": lounge},)




def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect("lounge_booker:login")

    context = {"bookings": Booking.objects.filter(user=request.user)} 
    return render(request, "my_bookings.html", context=context) 


def delete_booking(request, booking_id):
    if not request.user.is_authenticated:
        return redirect("lounge_booker:login")

    booking = get_object_or_404(Booking, pk=booking_id)

    if request.method == "POST":
        booking.delete()
        return redirect("lounge_booker:my-bookings")

    return render(request, "delete_booking.html", context={"booking": booking})


def update_booking(request, booking_id):
    if not request.user.is_authenticated:
        return redirect("lounge_booker:login")

    
    booking = get_object_or_404(Booking, pk=booking_id)

    booking_form = {"booking_form": BookingForm(booking.lounge, instance=booking)}

    if request.method == "POST":
        form = BookingForm(booking.lounge, request.POST, instance=booking)

        if form.is_valid():
            form.save()
            messages.info(request, f"Thank you, you have successfully updated your booking with {booking.lounge.name}")
            return redirect("lounge_booker:my-bookings")

    return render(request, "update_booking.html", context=booking_form)



