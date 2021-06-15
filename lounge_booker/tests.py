from django.test import TestCase

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import LoungeFactory, LoungeBookFactory, UserFactory
from .forms import BookingForm, UserForm
from .models import Lounge
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
