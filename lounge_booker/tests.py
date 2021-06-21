from django.http import response
from django.test import TestCase

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import LoungeFactory, LoungeBookFactory, UserFactory, BookingFactory, SettingFactory
from .forms import BookingForm, UserForm
from .models import Lounge, Table, Booking
from django.contrib.auth.forms import AuthenticationForm


class HomePageTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.lounge = LoungeFactory()


    def test_authentication(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
    

    def test_context_data(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        context = response.context["lounges"]

        self.assertEqual(list(context), list(Lounge.objects.all()))

      
    def test_template_rendered(self):
        self.client.force_login(self.user)
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


class LoginPageTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url = "/login"
        self.response = self.client.get(self.url)

    
    def test_blank_login_page(self):
        context_form = self.response.context["login_form"]

        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(context_form, AuthenticationForm)
        self.assertTemplateUsed(self.response, "login.html")


    def test_successful_login(self):
            data = {
                "username": self.user.username,
                "password": "top-secret",
            }
            response = self.client.post(self.url, data, follow=True)

            message = list(response.context.get("messages"))[0]
            self.assertEqual(message.tags, "info")
            self.assertTrue(
                f"Hello {self.user.username}, you are now logged in." in message.message
            )
            self.assertRedirects(response, "/", status_code=302)


    def test_unsuccessful_login(self):
        data = {
            "username": self.user.username,
            "password": "wrong-password",
        }
        response = self.client.post(self.url, data, follow=True)

        message = list(response.context.get("messages"))[0]
        self.assertEqual(message.tags, "error")
        self.assertTrue("Invalid username or password, please try again." in message.message)


class SignUpPageTests(TestCase):
    def setUp(self):
        self.url = "/signup"
        self.response = self.client.get(self.url)

    def test_blank_signup_form(self):
        context_form = self.response.context["register_form"]

        self.assertEqual(self.response.status_code, 200)
        self.assertIsInstance(context_form, UserForm)
        self.assertTemplateUsed(self.response, "signup.html")

    def test_successful_signup(self):
        data = {
            'first_name': "Tai", 
            'last_name': "Mansa",
            'username': "Tai-m",
            'email': "Taim@hotmail.com",
            'password1': "top-secret",
            'password2': "top-secret",
        }
        response = self.client.post(self.url, data, follow=True)

        message = list(response.context.get("messages"))[0]
        self.assertEqual(message.tags, "success")
        self.assertTrue("Your registration was succesful, thank you." in message.message)
        self.assertRedirects(response, "/", status_code=302)

    def test_unsuccesful_signup(self):
        data = {
            'first_name': "", 
            'last_name': "",
            'username': "",
            'email': "",
            'password1': "",
            'password2': "",
        }
        response = self.client.post(self.url, data, follow=True)

        message = list(response.context.get("messages"))[0]
        self.assertEqual(message.tags, "error")
        self.assertTrue(
            "Unsuccesful registration. Invalid information, please try again." in message.message
        )


class LogoutPageTests(TestCase):
    def setUp(self):
        self.url = "/logout"
        self.response = self.client.get(self.url, follow=True)

    def test_logout(self):
        message = list(self.response.context.get("messages"))[0]

        self.assertEqual(message.tags, "info")
        self.assertEqual(message.message, "You have logged out succesfully, see you soon.")
        self.assertRedirects(self.response, "/login", status_code=302)


class BookingLoungeTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.lounge = LoungeFactory()
        self.setting = SettingFactory(lounge=self.lounge, min_guest=2)
        self.table = LoungeBookFactory(lounge=self.lounge)
        self.url = f"/book-lounge/{self.lounge.id}"
        
        

    def test_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_invalid_lounge_id(self):
        self.client.force_login(self.user)
        url = "/book-lounge/99999"

        response = self.client.get(url, follow=True)
        message = list(response.context.get("messages"))[0]

        self.assertEqual(message.tags, "error")
        self.assertTrue("This lounge is not available, please select another." in message.message)
        self.assertRedirects(response, "/", status_code=302)

    def test_get_blank_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        context_form = response.context["booking_form"]

        self.assertTemplateUsed(response, "book_lounge.html")
        self.assertIsInstance(context_form, BookingForm)

    def test_successful_post(self):
        self.client.force_login(self.user)
        data ={
            "user" : self.user,
            "lounge": self.lounge.id,
            "table": self.lounge.tables.first().id,
            "total_guests": 2,
            "date": book_date(),        }

        response = self.client.post(self.url, data, follow=True)
        message = list(response.context.get("messages"))[0]
        self.assertEqual(message.tags, "info")
        self.assertTrue(f"You have succesfully booked with {self.lounge}. Enjoy!" in message.message)
        self.assertRedirects(response, "/", status_code=302)

    def test_table_queryset(self):
        LoungeBookFactory()

        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        context_form = response.context["booking_form"]

        current_queryset = context_form.fields["table"].queryset
        expected_queryset = Table.objects.filter(lounge_id=self.lounge.id)

        self.assertEqual(list(current_queryset), list(expected_queryset))

    def test_lounge_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        context_lounge = response.context["lounge"]

        self.assertEqual(context_lounge, self.lounge)


class MyBookingsTests(TestCase):
    def setUp(self):
        self.user1 = UserFactory(username="Jane")
        self.user2 = UserFactory(username="Jaxon")
        self.booking1 = BookingFactory(user=self.user1)
        self.booking2 = BookingFactory(user=self.user2)
        self.url = "/my-bookings"

    def test_authentication(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login", status_code=302)

    def test_template_rendered(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "my_bookings.html")
    
    def test_user1_context_data(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        context = response.context["bookings"]
        self.assertEqual(list(context), [self.booking1])

    def test_user2_context_data(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        context = response.context["bookings"]
        self.assertEqual(list(context), [self.booking2])


class DeleteMyBookingsTests(TestCase):
    def setUp(self):
        self.user = UserFactory(username="yanick")
        self.booking = BookingFactory()
        self.url = f"/delete-booking/{self.booking.id}"

    def test_authentication(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login", status_code=302)

    def test_booking_exists(self):
        self.client.force_login(self.user)
        url = "/delete-booking/12345"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_template_rendered(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "delete_booking.html")

    def test_delete_booking_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        context = response.context["booking"]

        self.assertEqual(context, self.booking)

    def test_successful_delete(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url)
        deleted_booking_queryset = Booking.objects.filter(id=self.booking.id)

        self.assertEqual(list(deleted_booking_queryset), [])
        self.assertRedirects(response, "/my-bookings", status_code=302)


class UpdateMyBookingsTests(TestCase):
    def setUp(self):
        self.user = UserFactory(username="nino")
        self.lounge = LoungeFactory()
        self.setting = SettingFactory(lounge=self.lounge, min_guest=2)
        self.table = LoungeBookFactory(lounge=self.lounge)
        self.booking = BookingFactory(
            user=self.user, lounge=self.lounge, table=self.table
        )
        self.url = f"/update-booking/{self.booking.id}"

    def test_authentication(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login", status_code=302)

   
    def test_booking_exists(self):
        self.client.force_login(self.user)
        url = "/update-booking/123456"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

   
    def test_template_rendered(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "update_booking.html")

   
    def test_update_booking_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        current_context = response.context["booking_form"]
        self.assertIsInstance(current_context, BookingForm)


    def test_successful_update(self):
        """ change table to duo table """
        self.client.force_login(self.user)
        duo_table = LoungeBookFactory(name="Duo", lounge=self.lounge)

        data = {
            "table": duo_table.id,
            "date": book_date(),
            "total_guests ": 2,
        }

        response = self.client.post(self.url, data, follow=True)
        message = list(response.context.get("messages"))[0]

        self.assertEqual(message.tags, "info")
        self.assertTrue(f"Thank you, you have successfully updated your booking with {self.booking.lounge.name}" in message.message)
        self.assertRedirects(response, "/my-bookings", status_code=302)


class BookingFormTest(TestCase):
    def setUp(self):
        self.capacity = 7
        self.min_guest = 3
        self.lounge= LoungeFactory()
        self.table = LoungeBookFactory(lounge=self.lounge, capacity=self.capacity)
        self.date = book_date()  # future date by default
        self.data = {"table": self.table.id, "date": self.date}
        self.setting = SettingFactory(lounge=self.lounge, min_guest=self.min_guest)

    def test_over_capacity_booking(self):
        self.data["total_guests"] = self.capacity + 1

        form = BookingForm(self.lounge, self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["total_guests"],
            [f"The maximum table capacity is {self.table.capacity}"]
        )

    
    def test_exact_capacity_booking(self):
        self.data["total_guests"] = self.capacity
        form = BookingForm(self.lounge, self.data)

        self.assertTrue(form.is_valid())

    def test_less_than_capacity_booking(self):
        self.data["total_guests"] = self.capacity - 1
        form = BookingForm(self.lounge, self.data)

        self.assertTrue(form.is_valid())

    def test_zero_capacity_booking(self):
        self.data["total_guests"] = 0  # lower number than capacity
        form = BookingForm(self.lounge, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["total_guests"],
            ["Please choose a valid number of guests for your order."],
        )

    def test_exact_min_guest(self):
        self.data["total_guests"] = self.min_guest
        form = BookingForm(self.lounge, self.data)
        
        self.assertTrue(form.is_valid())


    def test_below_min_guest(self):
        self.data["total_guests"] = self.min_guest -1
        form = BookingForm(self.lounge, self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["total_guests"],
            [f"The minimum guests per booking is: {self.min_guest}"])


    def test_booking_in_the_past(self):
        self.data["date"] = book_date(days=3, past=True)
        form = BookingForm(self.lounge, self.data)

        self.assertEquals(form.errors["date"], ["Please choose a date and time that is in the future, thank you."])
        self.assertFalse(form.is_valid())







def book_date(days=3, hours=1, minutes=30, past=False):
    today = datetime.datetime.today()
    delta = datetime.timedelta(days, hours, minutes)
    date = today - delta if past else today + delta

    return date.strftime("%Y-%m-%dT%H:%M")

