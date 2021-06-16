from django.test import TestCase

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import LoungeFactory, LoungeBookFactory, UserFactory
from .forms import BookingForm, UserForm
from .models import Lounge, Table
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
            "date": (datetime.datetime.today() + datetime.timedelta(days=3)).strftime(
                "%Y-%m-%dT%H:%M"
            ),        }

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