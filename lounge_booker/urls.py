from django.urls import path

from . import views 

app_name = "lounge_booker"

urlpatterns = [
    path("", views.home_page, name="home"),
    path("login", views.login_page, name="login"),
    path("logout", views.logout_page, name="logout"),
    path("signup", views.signup_page, name="signup"),
    path("book-lounge/<int:lounge_id>", views.book_lounge, name="book-lounge"),
    path("my-bookings", views.my_bookings, name="my-bookings"),
    path("delete-booking/<int:booking_id>", views.delete_booking, name="delete-booking"),
    path("update-booking/<int:booking_id>", views.update_booking, name="update-booking"),

]
