from django.test import TestCase

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import LoungeFactory, LoungeBookFactory, UserFactory
from .forms import BookingForm
from .models import Lounge


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


