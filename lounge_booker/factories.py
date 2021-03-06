import datetime

import factory
from django.contrib.auth.models import User

from . import models

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = "jacob"
    email = "jacob@test.com"
    password = factory.PostGenerationMethodCall("set_password", "top-secret")


class LoungeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Lounge

    name = "Familia Lounge"
    address1 = "20 Temple Road"
    address2 = "London"
    postcode = "E17 8BL"


class LoungeBookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Table

    lounge = factory.SubFactory(LoungeFactory)
    name = "Corner Table"
    capacity = 6


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Booking

    user = factory.SubFactory(UserFactory)
    lounge = factory.SubFactory(LoungeFactory)
    table = factory.SubFactory(LoungeBookFactory)
    date = datetime.date.today() + datetime.timedelta(days=1)  # tomorrow
    total_guests = 3



class BusinessHourFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BusinessHour

    lounge = factory.SubFactory(LoungeFactory)
    day = 1
    start_time = datetime.time(9, 30, 00)
    finish_time = datetime.time(17, 00, 00)
    closed = False


class SettingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Setting

    lounge = factory.SubFactory(LoungeFactory)
    min_guest = 2
